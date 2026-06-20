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
    public MainWindow()
    {
        InitializeComponent();

        // POC: サーバは fastapi dev の既定ポート 8000 を想定。
        var http = new HttpClient { BaseAddress = new Uri("http://localhost:8000") };
        DataContext = new ProductListViewModel(new ProductApiClient(http));
    }
}
