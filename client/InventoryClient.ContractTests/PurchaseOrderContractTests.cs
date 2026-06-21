using System.Net.Http;
using InventoryClient.Core.Api;
using InventoryClient.Core.Models;
using Xunit;

namespace InventoryClient.ContractTests;

/// <summary>発注→入荷フローの契約を実サーバで検証する(#0014)。</summary>
[Collection("server")]
public class PurchaseOrderContractTests
{
    private readonly ServerFixture _server;

    public PurchaseOrderContractTests(ServerFixture server) => _server = server;

    private HttpClient NewHttp() => new() { BaseAddress = new Uri(_server.BaseAddress) };

    private static string NewSku() => "PO-" + Guid.NewGuid().ToString("N")[..6];

    [Fact]
    public async Task Order_then_receive_increases_product_stock()
    {
        var products = new ProductApiClient(NewHttp());
        var orders = new PurchaseOrderApiClient(NewHttp());
        var sku = NewSku();
        await products.RegisterProductAsync(new ProductCreateRequest(sku, "ねじ", 0));

        var order = await orders.CreateOrderAsync(new PurchaseOrderCreateRequest(sku, 5));
        Assert.Equal("ordered", order.Status);

        var received = await orders.ReceiveOrderAsync(order.Id);
        Assert.Equal("received", received.Status);

        // 入荷で商品在庫が発注数だけ増えている
        var all = await products.ListProductsAsync();
        Assert.Equal(5, all.Single(p => p.Sku == sku).Quantity);
    }

    [Fact]
    public async Task Double_receive_throws()
    {
        var products = new ProductApiClient(NewHttp());
        var orders = new PurchaseOrderApiClient(NewHttp());
        var sku = NewSku();
        await products.RegisterProductAsync(new ProductCreateRequest(sku, "ボルト", 0));
        var order = await orders.CreateOrderAsync(new PurchaseOrderCreateRequest(sku, 3));
        await orders.ReceiveOrderAsync(order.Id);

        // 2 度目の入荷は 409 → クライアントは例外
        await Assert.ThrowsAnyAsync<HttpRequestException>(() => orders.ReceiveOrderAsync(order.Id));
    }
}
