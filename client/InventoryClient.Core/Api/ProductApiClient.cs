using System.Net.Http.Json;
using InventoryClient.Core.Models;

namespace InventoryClient.Core.Api;

/// <summary>
/// 実際の HTTP 実装。System.Net.Http.Json の既定(Web)は camelCase かつ大小文字を無視するため、
/// FastAPI の {"sku","name","quantity"} と C# の Sku/Name/Quantity が自動で対応する。
/// </summary>
public sealed class ProductApiClient : IProductApiClient
{
    private readonly HttpClient _http;

    public ProductApiClient(HttpClient http) => _http = http;

    public async Task<IReadOnlyList<ProductDto>> ListProductsAsync(CancellationToken ct = default)
    {
        var products = await _http.GetFromJsonAsync<List<ProductDto>>("/products", ct);
        return products ?? new List<ProductDto>();
    }

    public async Task<ProductDto> RegisterProductAsync(ProductCreateRequest request, CancellationToken ct = default)
    {
        var response = await _http.PostAsJsonAsync("/products", request, ct);
        response.EnsureSuccessStatusCode();
        var dto = await response.Content.ReadFromJsonAsync<ProductDto>(ct);
        return dto!;
    }

    public Task<ProductDto> ReceiveAsync(string sku, int amount, CancellationToken ct = default) =>
        PostStockChangeAsync(sku, "receive", amount, ct);

    public Task<ProductDto> ShipAsync(string sku, int amount, CancellationToken ct = default) =>
        PostStockChangeAsync(sku, "ship", amount, ct);

    private async Task<ProductDto> PostStockChangeAsync(string sku, string action, int amount, CancellationToken ct)
    {
        var response = await _http.PostAsJsonAsync($"/products/{sku}/{action}", new { amount }, ct);
        response.EnsureSuccessStatusCode();
        var dto = await response.Content.ReadFromJsonAsync<ProductDto>(ct);
        return dto!;
    }
}
