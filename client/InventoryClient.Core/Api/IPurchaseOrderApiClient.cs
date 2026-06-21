using InventoryClient.Core.Models;

namespace InventoryClient.Core.Api;

/// <summary>サーバの発注APIへのアクセス。</summary>
public interface IPurchaseOrderApiClient
{
    Task<PurchaseOrderDto> CreateOrderAsync(PurchaseOrderCreateRequest request, CancellationToken ct = default);

    Task<IReadOnlyList<PurchaseOrderDto>> ListOrdersAsync(CancellationToken ct = default);

    Task<PurchaseOrderDto> ReceiveOrderAsync(string orderId, CancellationToken ct = default);
}
