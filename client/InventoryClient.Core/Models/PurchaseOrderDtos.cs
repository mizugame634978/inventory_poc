namespace InventoryClient.Core.Models;

/// <summary>発注(GET/POST の応答)。status は "ordered" / "received"。</summary>
public record PurchaseOrderDto(string Id, string Sku, int Quantity, string Status);

/// <summary>発注作成リクエスト(POST /purchase-orders の本文)。</summary>
public record PurchaseOrderCreateRequest(string Sku, int Quantity);
