using System.Diagnostics;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;
using InventoryClient;
using InventoryClient.Core.Api;
using InventoryClient.Core.Models;
using InventoryClient.Core.ViewModels;
using NSubstitute;
using Xunit;

namespace InventoryClient.UiTests;

/// <summary>
/// in-process の UI テスト。Window を実際に生成しレイアウトを走らせ、
/// XAML バインディングが壊れていないことを検証する(ViewModel テストでは捕まえられない劣化)。
/// タブごとに表示を切り替えて、両タブのバインディングを実体化させて検査する。
/// </summary>
public class MainWindowBindingTests
{
    /// <summary>WPF の DataBinding トレースに出るバインディング失敗を捕捉するリスナ。</summary>
    private sealed class BindingErrorListener : TraceListener
    {
        public List<string> Messages { get; } = new();

        public override void Write(string? message) { }

        public override void WriteLine(string? message)
        {
            if (!string.IsNullOrEmpty(message))
            {
                Messages.Add(message);
            }
        }
    }

    private static MainViewModel CreateMainViewModel()
    {
        var productApi = Substitute.For<IProductApiClient>();
        productApi.ListProductsAsync().Returns(new List<ProductDto>
        {
            new("A-1", "ねじ", 5),
            new("B-2", "ボルト", 0),
        });
        var orderApi = Substitute.For<IPurchaseOrderApiClient>();
        orderApi.ListOrdersAsync().Returns(new List<PurchaseOrderDto>
        {
            new("id1", "A-1", 3, "ordered"),
        });
        return new MainViewModel(
            new ProductListViewModel(productApi),
            new PurchaseOrderViewModel(orderApi));
    }

    /// <summary>残った Dispatcher 作業を処理してレイアウト/バインディングを確定させる。</summary>
    private static void DrainDispatcher()
    {
        var frame = new DispatcherFrame();
        Dispatcher.CurrentDispatcher.BeginInvoke(
            DispatcherPriority.ContextIdle, new Action(() => frame.Continue = false));
        Dispatcher.PushFrame(frame);
    }

    [WpfFact]
    public async Task Both_tabs_bind_without_errors_and_show_rows()
    {
        // バインディング失敗を捕捉する準備
        PresentationTraceSources.Refresh();
        var listener = new BindingErrorListener();
        PresentationTraceSources.DataBindingSource.Listeners.Add(listener);
        PresentationTraceSources.DataBindingSource.Switch.Level = SourceLevels.Error | SourceLevels.Warning;

        MainWindow? window = null;
        try
        {
            var vm = CreateMainViewModel();
            window = new MainWindow(vm)
            {
                Width = 760,
                Height = 480,
                // 画面の邪魔をしないよう画面外に出して表示する。
                WindowStartupLocation = WindowStartupLocation.Manual,
                Left = -10000,
                Top = -10000,
                ShowInTaskbar = false,
            };
            window.Show();
            DrainDispatcher();

            await vm.Products.LoadAsync();
            await vm.Orders.LoadAsync();

            // 各タブを順に選択して、両タブのセル(列)バインディングを実体化させる。
            var tabs = (TabControl)window.FindName("MainTabs")!;
            for (var i = 0; i < tabs.Items.Count; i++)
            {
                tabs.SelectedIndex = i;
                window.UpdateLayout();
                DrainDispatcher();
            }

            // 行数の確認(ItemsSource バインディングが生きている証拠)
            var productsGrid = (DataGrid)window.FindName("ProductsGrid")!;
            var ordersGrid = (DataGrid)window.FindName("OrdersGrid")!;
            Assert.Equal(2, productsGrid.Items.Count);
            Assert.Equal(1, ordersGrid.Items.Count);

            Assert.True(
                listener.Messages.Count == 0,
                "バインディングエラーが発生しました:\n" + string.Join("\n", listener.Messages));
        }
        finally
        {
            window?.Close();
            PresentationTraceSources.DataBindingSource.Listeners.Remove(listener);
        }
    }
}
