using System.Net.Http.Json;
using InventoryClient.Core.Models;

namespace InventoryClient.Core.Api;

public sealed class PurchaseOrderApiClient : IPurchaseOrderApiClient
{
    private readonly HttpClient _http;

    public PurchaseOrderApiClient(HttpClient http) => _http = http;

    public async Task<PurchaseOrderDto> CreateOrderAsync(PurchaseOrderCreateRequest request, CancellationToken ct = default)
    {
        var response = await _http.PostAsJsonAsync("/purchase-orders", request, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<PurchaseOrderDto>(ct))!;
    }

    public async Task<IReadOnlyList<PurchaseOrderDto>> ListOrdersAsync(CancellationToken ct = default)
    {
        var orders = await _http.GetFromJsonAsync<List<PurchaseOrderDto>>("/purchase-orders", ct);
        return orders ?? new List<PurchaseOrderDto>();
    }

    public async Task<PurchaseOrderDto> ReceiveOrderAsync(string orderId, CancellationToken ct = default)
    {
        var response = await _http.PostAsync($"/purchase-orders/{orderId}/receive", content: null, ct);
        response.EnsureSuccessStatusCode();
        return (await response.Content.ReadFromJsonAsync<PurchaseOrderDto>(ct))!;
    }
}
