using System.Net.Http;
using System.Windows;
using InventoryClient.Core.Api;
using InventoryClient.Core.ViewModels;

namespace InventoryClient;

/// <summary>
/// View は薄い層。ここでは ViewModel に依存を組み立てて DataContext に渡すだけで、業務ロジックは持たない。
/// </summary>
public partial class MainWindow : Window
{
    // 実行時用: 既定の実サーバ構成で ViewModel を組み立てる。
    public MainWindow() : this(CreateDefaultViewModel())
    {
    }

    // テスト用: モックを仕込んだ ViewModel を注入できる。
    public MainWindow(MainViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }

    private static MainViewModel CreateDefaultViewModel()
    {
        // POC: サーバは fastapi dev の既定ポート 8000 を想定。商品・発注で HttpClient を共有する。
        // localhost ではなく 127.0.0.1 を使う(localhost は IPv6 ::1 を先に試して 1 秒ほど待つことがある)。
        var http = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:8000") };
        var products = new ProductListViewModel(new ProductApiClient(http));
        var orders = new PurchaseOrderViewModel(new PurchaseOrderApiClient(http));
        return new MainViewModel(products, orders);
    }
}
