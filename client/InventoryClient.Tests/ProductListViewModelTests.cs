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
}
