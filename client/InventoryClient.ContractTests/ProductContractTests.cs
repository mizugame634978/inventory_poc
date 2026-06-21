using System.Net.Http;
using InventoryClient.Core.Api;
using InventoryClient.Core.Models;
using Xunit;

namespace InventoryClient.ContractTests;

/// <summary>
/// 実サーバ相手に ProductApiClient の「契約」を検証する。
/// ViewModel テスト(モック)では捕まえられない、JSONフィールド名・型・HTTPステータスのズレを検出する。
/// 1つのサーバをクラス内テストで共有する(IClassFixture)。テスト間の衝突を避けるため SKU は毎回ユニーク。
/// </summary>
public class ProductContractTests : IClassFixture<ServerFixture>
{
    private readonly ServerFixture _server;

    public ProductContractTests(ServerFixture server) => _server = server;

    private ProductApiClient NewClient() =>
        new(new HttpClient { BaseAddress = new Uri(_server.BaseAddress) });

    private static string NewSku() => "C-" + Guid.NewGuid().ToString("N")[..6];

    [Fact]
    public async Task Register_roundtrip_matches_fields()
    {
        var api = NewClient();
        var sku = NewSku();

        var created = await api.RegisterProductAsync(new ProductCreateRequest(sku, "ねじ", 2));

        // 双方向シリアライズ(C# PascalCase ↔ サーバ lower)が成立していることの確認
        Assert.Equal(sku, created.Sku);
        Assert.Equal("ねじ", created.Name);
        Assert.Equal(2, created.Quantity);
    }

    [Fact]
    public async Task Receive_and_ship_update_quantity()
    {
        var api = NewClient();
        var sku = NewSku();
        await api.RegisterProductAsync(new ProductCreateRequest(sku, "ボルト", 0));

        var afterReceive = await api.ReceiveAsync(sku, 5);
        Assert.Equal(5, afterReceive.Quantity);

        var afterShip = await api.ShipAsync(sku, 2);
        Assert.Equal(3, afterShip.Quantity);
    }

    [Fact]
    public async Task Ship_insufficient_stock_throws()
    {
        var api = NewClient();
        var sku = NewSku();
        await api.RegisterProductAsync(new ProductCreateRequest(sku, "ナット", 1));

        // サーバは 409 を返し、クライアントは EnsureSuccessStatusCode で例外にする(エラー契約)
        await Assert.ThrowsAnyAsync<HttpRequestException>(() => api.ShipAsync(sku, 5));
    }

    [Fact]
    public async Task List_contains_registered()
    {
        var api = NewClient();
        var sku = NewSku();
        await api.RegisterProductAsync(new ProductCreateRequest(sku, "ワッシャ", 1));

        var all = await api.ListProductsAsync();

        Assert.Contains(all, p => p.Sku == sku);
    }
}
