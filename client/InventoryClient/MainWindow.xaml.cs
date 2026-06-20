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
    public MainWindow(ProductListViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }

    private static ProductListViewModel CreateDefaultViewModel()
    {
        // POC: サーバは fastapi dev の既定ポート 8000 を想定。
        var http = new HttpClient { BaseAddress = new Uri("http://localhost:8000") };
        return new ProductListViewModel(new ProductApiClient(http));
    }
}
