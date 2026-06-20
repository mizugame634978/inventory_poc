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

    private static ProductListViewModel CreateViewModelWith(params ProductDto[] products)
    {
        var api = Substitute.For<IProductApiClient>();
        api.ListProductsAsync().Returns(products.ToList());
        return new ProductListViewModel(api);
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
    public async Task Loaded_grid_shows_expected_rows_with_no_binding_errors()
    {
        // バインディング失敗を捕捉する準備
        PresentationTraceSources.Refresh();
        var listener = new BindingErrorListener();
        PresentationTraceSources.DataBindingSource.Listeners.Add(listener);
        PresentationTraceSources.DataBindingSource.Switch.Level = SourceLevels.Error | SourceLevels.Warning;

        MainWindow? window = null;
        try
        {
            var vm = CreateViewModelWith(
                new ProductDto("A-1", "ねじ", 5),
                new ProductDto("B-2", "ボルト", 0));
            window = new MainWindow(vm)
            {
                Width = 720,
                Height = 450,
                // 画面の邪魔をしないよう画面外に出して表示する。
                WindowStartupLocation = WindowStartupLocation.Manual,
                Left = -10000,
                Top = -10000,
                ShowInTaskbar = false,
            };

            // DataGrid の行(セル)を実体化させるには実描画が要る。Show して描画パスを回す。
            window.Show();
            DrainDispatcher();

            await vm.LoadAsync();

            // 行とセルのバインディングを確定させる
            window.UpdateLayout();
            DrainDispatcher();

            var grid = (DataGrid)window.FindName("ProductsGrid")!;
            Assert.Equal(2, grid.Items.Count);

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
