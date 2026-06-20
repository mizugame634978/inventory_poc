namespace InventoryClient.Core.Models;

/// <summary>サーバから受け取る商品(GET /products の要素 / POST /products の応答)。</summary>
public record ProductDto(string Sku, string Name, int Quantity);

/// <summary>商品登録リクエスト(POST /products の本文)。</summary>
public record ProductCreateRequest(string Sku, string Name, int Quantity);
