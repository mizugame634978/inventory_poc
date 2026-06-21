using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using InventoryClient.Core.Api;
using InventoryClient.Core.Models;

namespace InventoryClient.Core.ViewModels;

/// <summary>
/// 発注画面の状態とふるまい。発注の一覧・新規発注・選択発注の入荷を扱う。
/// ProductListViewModel と同じく WPF 非依存で、テストから直接検証できる。
/// </summary>
public partial class PurchaseOrderViewModel : ObservableObject, IRefreshableViewModel
{
    private readonly IPurchaseOrderApiClient _api;

    public ObservableCollection<PurchaseOrderDto> Orders { get; } = new();

    [ObservableProperty]
    private bool _isLoading;

    [ObservableProperty]
    private string? _errorMessage;

    // 新規発注の入力
    [ObservableProperty]
    private string _newSku = "";

    [ObservableProperty]
    private int _newQuantity = 1;

    [ObservableProperty]
    private PurchaseOrderDto? _selectedOrder;

    public PurchaseOrderViewModel(IPurchaseOrderApiClient api) => _api = api;

    [RelayCommand]
    public async Task LoadAsync()
    {
        IsLoading = true;
        ErrorMessage = null;
        try
        {
            var orders = await _api.ListOrdersAsync();
            Orders.Clear();
            foreach (var o in orders)
            {
                Orders.Add(o);
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = $"発注の読み込みに失敗しました: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }

    [RelayCommand]
    public async Task CreateAsync()
    {
        if (string.IsNullOrWhiteSpace(NewSku))
        {
            ErrorMessage = "SKU は必須です";
            return;
        }
        if (NewQuantity < 1)
        {
            ErrorMessage = "発注数は 1 以上である必要があります";
            return;
        }

        IsLoading = true;
        ErrorMessage = null;
        try
        {
            await _api.CreateOrderAsync(new PurchaseOrderCreateRequest(NewSku, NewQuantity));
            NewSku = "";
            NewQuantity = 1;
            await LoadAsync();
        }
        catch (Exception ex)
        {
            ErrorMessage = $"発注に失敗しました: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }

    [RelayCommand]
    public async Task ReceiveAsync()
    {
        if (SelectedOrder is null)
        {
            ErrorMessage = "入荷する発注を選択してください";
            return;
        }

        IsLoading = true;
        ErrorMessage = null;
        try
        {
            await _api.ReceiveOrderAsync(SelectedOrder.Id);
            await LoadAsync(); // status を最新化(ordered → received)
        }
        catch (Exception ex)
        {
            ErrorMessage = $"入荷に失敗しました: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }
}
