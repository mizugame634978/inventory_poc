using InventoryClient.Core.Models;

namespace InventoryClient.Core.Api;

/// <summary>
/// サーバの商品APIへのアクセス。ViewModel はこの「インターフェース」に依存する(具象 HttpClient ではない)。
/// これにより、テストではモックに差し替えてネットワーク無しで ViewModel を検証できる(依存性逆転)。
/// </summary>
public interface IProductApiClient
{
    Task<IReadOnlyList<ProductDto>> ListProductsAsync(CancellationToken ct = default);

    Task<ProductDto> RegisterProductAsync(ProductCreateRequest request, CancellationToken ct = default);
}
