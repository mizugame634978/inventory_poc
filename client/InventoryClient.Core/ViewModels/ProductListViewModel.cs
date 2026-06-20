using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InventoryClient.Core.Api;
using InventoryClient.Core.Models;

namespace InventoryClient.Core.ViewModels;

/// <summary>
/// 商品一覧画面の状態とふるまい。View(XAML)はこの ViewModel をバインドするだけで、ロジックを持たない。
/// WPF アセンブリに依存しないため、テストプロジェクト(net10.0)からそのまま検証できる。
/// </summary>
public partial class ProductListViewModel : ObservableObject
{
    private readonly IProductApiClient _api;

    public ObservableCollection<ProductDto> Products { get; } = new();

    [ObservableProperty]
    private bool _isLoading;

    [ObservableProperty]
    private string? _errorMessage;

    // 登録フォームの入力
    [ObservableProperty]
    private string _newSku = "";

    [ObservableProperty]
    private string _newName = "";

    [ObservableProperty]
    private int _newQuantity;

    // 入荷/出荷の対象と数量
    [ObservableProperty]
    private ProductDto? _selectedProduct;

    [ObservableProperty]
    private int _operationAmount = 1;

    public ProductListViewModel(IProductApiClient api) => _api = api;

    [RelayCommand]
    public async Task LoadAsync()
    {
        IsLoading = true;
        ErrorMessage = null;
        try
        {
            var products = await _api.ListProductsAsync();
            Products.Clear();
            foreach (var p in products)
            {
                Products.Add(p);
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = $"読み込みに失敗しました: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }

    [RelayCommand]
    public async Task RegisterAsync()
    {
        // 入力検証は ViewModel の責務。不正なら API を呼ばない。
        if (string.IsNullOrWhiteSpace(NewSku) || string.IsNullOrWhiteSpace(NewName))
        {
            ErrorMessage = "SKU と 名前 は必須です";
            return;
        }

        IsLoading = true;
        ErrorMessage = null;
        try
        {
            await _api.RegisterProductAsync(new ProductCreateRequest(NewSku, NewName, NewQuantity));
            NewSku = "";
            NewName = "";
            NewQuantity = 0;
            await LoadAsync(); // 登録後に一覧を最新化する
        }
        catch (Exception ex)
        {
            ErrorMessage = $"登録に失敗しました: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }

    [RelayCommand]
    public Task ReceiveAsync() => ExecuteStockOpAsync("入荷", sku => _api.ReceiveAsync(sku, OperationAmount));

    [RelayCommand]
    public Task ShipAsync() => ExecuteStockOpAsync("出荷", sku => _api.ShipAsync(sku, OperationAmount));

    // 入荷/出荷の共通処理: 対象選択と数量を検証し、API を呼び、一覧を再読込する。
    private async Task ExecuteStockOpAsync(string label, Func<string, Task> operation)
    {
        if (SelectedProduct is null)
        {
            ErrorMessage = $"{label}する商品を選択してください";
            return;
        }
        if (OperationAmount < 1)
        {
            ErrorMessage = "数量は 1 以上である必要があります";
            return;
        }

        IsLoading = true;
        ErrorMessage = null;
        try
        {
            await operation(SelectedProduct.Sku);
            await LoadAsync(); // 在庫の最新値を反映する
        }
        catch (Exception ex)
        {
            ErrorMessage = $"{label}に失敗しました: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }
}
