using InventoryClient.Core.Api;
using InventoryClient.Core.Models;
using InventoryClient.Core.ViewModels;
using NSubstitute;
using NSubstitute.ExceptionExtensions;
using Xunit;

namespace InventoryClient.Tests;

public class ProductListViewModelTests
{
    [Fact]
    public async Task LoadAsync_populates_Products_from_api()
    {
        var api = Substitute.For<IProductApiClient>();
        api.ListProductsAsync().Returns(new List<ProductDto>
        {
            new("A-1", "ねじ", 5),
            new("B-2", "ボルト", 0),
        });
        var vm = new ProductListViewModel(api);

        await vm.LoadAsync();

        Assert.Equal(2, vm.Products.Count);
        Assert.Contains(vm.Products, p => p.Sku == "A-1");
        Assert.False(vm.IsLoading);
        Assert.Null(vm.ErrorMessage);
    }

    [Fact]
    public async Task LoadAsync_sets_ErrorMessage_and_keeps_Products_intact_on_failure()
    {
        var api = Substitute.For<IProductApiClient>();
        api.ListProductsAsync().Throws(new Exception("boom"));
        var vm = new ProductListViewModel(api);

        await vm.LoadAsync();

        Assert.NotNull(vm.ErrorMessage);
        Assert.Empty(vm.Products);
        Assert.False(vm.IsLoading);
    }

    [Fact]
    public async Task RegisterAsync_calls_register_then_reloads()
    {
        var api = Substitute.For<IProductApiClient>();
        api.ListProductsAsync().Returns(new List<ProductDto>());
        var vm = new ProductListViewModel(api)
        {
            NewSku = "A-1",
            NewName = "ねじ",
            NewQuantity = 3,
        };

        await vm.RegisterAsync();

        await api.Received(1).RegisterProductAsync(
            Arg.Is<ProductCreateRequest>(r => r.Sku == "A-1" && r.Name == "ねじ" && r.Quantity == 3));
        await api.Received(1).ListProductsAsync();
        Assert.Equal("", vm.NewSku); // 登録後に入力がクリアされる
    }

    [Fact]
    public async Task RegisterAsync_with_empty_sku_does_not_call_api()
    {
        var api = Substitute.For<IProductApiClient>();
        var vm = new ProductListViewModel(api)
        {
            NewSku = "",
            NewName = "ねじ",
        };

        await vm.RegisterAsync();

        await api.DidNotReceive().RegisterProductAsync(Arg.Any<ProductCreateRequest>());
        Assert.NotNull(vm.ErrorMessage);
    }

    [Fact]
    public async Task ReceiveAsync_calls_api_then_reloads()
    {
        var api = Substitute.For<IProductApiClient>();
        api.ListProductsAsync().Returns(new List<ProductDto>());
        var vm = new ProductListViewModel(api)
        {
            SelectedProduct = new ProductDto("A-1", "ねじ", 2),
            OperationAmount = 3,
        };

        await vm.ReceiveAsync();

        await api.Received(1).ReceiveAsync("A-1", 3);
        await api.Received(1).ListProductsAsync();
        Assert.Null(vm.ErrorMessage);
    }

    [Fact]
    public async Task StockOp_without_selection_does_not_call_api()
    {
        var api = Substitute.For<IProductApiClient>();
        var vm = new ProductListViewModel(api) { SelectedProduct = null, OperationAmount = 1 };

        await vm.ShipAsync();

        await api.DidNotReceive().ShipAsync(Arg.Any<string>(), Arg.Any<int>());
        Assert.NotNull(vm.ErrorMessage);
    }

    [Fact]
    public async Task ShipAsync_sets_ErrorMessage_on_api_failure()
    {
        var api = Substitute.For<IProductApiClient>();
        api.ShipAsync("A-1", 99).Throws(new Exception("在庫不足"));
        var vm = new ProductListViewModel(api)
        {
            SelectedProduct = new ProductDto("A-1", "ねじ", 1),
            OperationAmount = 99,
        };

        await vm.ShipAsync();

        Assert.NotNull(vm.ErrorMessage);
        // 失敗時は一覧の再読込をしない(壊れた状態を表示しない)
        await api.DidNotReceive().ListProductsAsync();
    }
}
