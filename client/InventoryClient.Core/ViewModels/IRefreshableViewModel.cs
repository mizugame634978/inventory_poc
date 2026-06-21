namespace InventoryClient.Core.ViewModels;

/// <summary>
/// 画面(タブ)を表示したときに自動で再読み込みできる ViewModel。
/// View 側はこの契約だけ知っていれば、タブの種類によらず一様に LoadAsync を呼べる。
/// </summary>
public interface IRefreshableViewModel
{
    Task LoadAsync();
}
