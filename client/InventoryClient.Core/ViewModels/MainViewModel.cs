namespace InventoryClient.Core.ViewModels;

/// <summary>
/// 画面全体(タブ)の親 ViewModel。商品タブと発注タブの ViewModel を束ねるだけ。
/// </summary>
public sealed class MainViewModel
{
    public ProductListViewModel Products { get; }

    public PurchaseOrderViewModel Orders { get; }

    public MainViewModel(ProductListViewModel products, PurchaseOrderViewModel orders)
    {
        Products = products;
        Orders = orders;
    }
}
