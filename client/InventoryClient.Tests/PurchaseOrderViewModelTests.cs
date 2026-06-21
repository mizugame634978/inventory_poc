using InventoryClient.Core.Api;
using InventoryClient.Core.Models;
using InventoryClient.Core.ViewModels;
using NSubstitute;
using NSubstitute.ExceptionExtensions;
using Xunit;

namespace InventoryClient.Tests;

public class PurchaseOrderViewModelTests
{
    [Fact]
    public async Task LoadAsync_populates_Orders()
    {
        var api = Substitute.For<IPurchaseOrderApiClient>();
        api.ListOrdersAsync().Returns(new List<PurchaseOrderDto>
        {
            new("id1", "A-1", 5, "ordered"),
        });
        var vm = new PurchaseOrderViewModel(api);

        await vm.LoadAsync();

        Assert.Single(vm.Orders);
        Assert.Null(vm.ErrorMessage);
    }

    [Fact]
    public async Task CreateAsync_calls_api_then_reloads()
    {
        var api = Substitute.For<IPurchaseOrderApiClient>();
        api.ListOrdersAsync().Returns(new List<PurchaseOrderDto>());
        var vm = new PurchaseOrderViewModel(api) { NewSku = "A-1", NewQuantity = 3 };

        await vm.CreateAsync();

        await api.Received(1).CreateOrderAsync(
            Arg.Is<PurchaseOrderCreateRequest>(r => r.Sku == "A-1" && r.Quantity == 3));
        await api.Received(1).ListOrdersAsync();
        Assert.Equal("", vm.NewSku);
    }

    [Fact]
    public async Task CreateAsync_with_empty_sku_does_not_call_api()
    {
        var api = Substitute.For<IPurchaseOrderApiClient>();
        var vm = new PurchaseOrderViewModel(api) { NewSku = "", NewQuantity = 1 };

        await vm.CreateAsync();

        await api.DidNotReceive().CreateOrderAsync(Arg.Any<PurchaseOrderCreateRequest>());
        Assert.NotNull(vm.ErrorMessage);
    }

    [Fact]
    public async Task ReceiveAsync_calls_api_then_reloads()
    {
        var api = Substitute.For<IPurchaseOrderApiClient>();
        api.ListOrdersAsync().Returns(new List<PurchaseOrderDto>());
        var vm = new PurchaseOrderViewModel(api)
        {
            SelectedOrder = new PurchaseOrderDto("id1", "A-1", 5, "ordered"),
        };

        await vm.ReceiveAsync();

        await api.Received(1).ReceiveOrderAsync("id1");
        await api.Received(1).ListOrdersAsync();
    }

    [Fact]
    public async Task ReceiveAsync_without_selection_does_not_call_api()
    {
        var api = Substitute.For<IPurchaseOrderApiClient>();
        var vm = new PurchaseOrderViewModel(api) { SelectedOrder = null };

        await vm.ReceiveAsync();

        await api.DidNotReceive().ReceiveOrderAsync(Arg.Any<string>());
        Assert.NotNull(vm.ErrorMessage);
    }

    [Fact]
    public async Task ReceiveAsync_sets_ErrorMessage_on_api_failure()
    {
        var api = Substitute.For<IPurchaseOrderApiClient>();
        api.ReceiveOrderAsync("id1").Throws(new Exception("既に入荷済み"));
        var vm = new PurchaseOrderViewModel(api)
        {
            SelectedOrder = new PurchaseOrderDto("id1", "A-1", 5, "received"),
        };

        await vm.ReceiveAsync();

        Assert.NotNull(vm.ErrorMessage);
        await api.DidNotReceive().ListOrdersAsync(); // 失敗時は再読込しない
    }
}
