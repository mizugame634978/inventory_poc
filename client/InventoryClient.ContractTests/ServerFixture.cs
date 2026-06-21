using System.Diagnostics;
using System.Net;
using System.Net.Sockets;
using System.Text;

namespace InventoryClient.ContractTests;

/// <summary>
/// 実際の FastAPI サーバをサブプロセスで起動し、契約テストから使えるようにするフィクスチャ。
/// 空きポートと一時 DB(INVENTORY_DB)を使うので、他の実行や本番DBと干渉しない。
/// </summary>
public sealed class ServerFixture : IAsyncLifetime
{
    private Process? _process;
    private string _dbPath = "";
    private readonly StringBuilder _log = new();

    public string BaseAddress { get; private set; } = "";

    public async Task InitializeAsync()
    {
        var serverDir = Path.Combine(FindRepoRoot(), "server");
        var port = FreePort();
        BaseAddress = $"http://127.0.0.1:{port}";
        _dbPath = Path.Combine(Path.GetTempPath(), $"inventory_contract_{Guid.NewGuid():N}.db");

        var psi = new ProcessStartInfo
        {
            FileName = "uv",
            WorkingDirectory = serverDir,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        psi.ArgumentList.Add("run");
        psi.ArgumentList.Add("uvicorn");
        psi.ArgumentList.Add("app.main:app");
        psi.ArgumentList.Add("--host");
        psi.ArgumentList.Add("127.0.0.1");
        psi.ArgumentList.Add("--port");
        psi.ArgumentList.Add(port.ToString());
        psi.Environment["INVENTORY_DB"] = _dbPath;

        _process = new Process { StartInfo = psi };
        // パイプバッファが詰まってサーバが止まらないよう、出力は非同期で吸い出す。
        _process.OutputDataReceived += (_, e) => { if (e.Data != null) lock (_log) { _log.AppendLine(e.Data); } };
        _process.ErrorDataReceived += (_, e) => { if (e.Data != null) lock (_log) { _log.AppendLine(e.Data); } };
        _process.Start();
        _process.BeginOutputReadLine();
        _process.BeginErrorReadLine();

        await WaitUntilReadyAsync();
    }

    public Task DisposeAsync()
    {
        try
        {
            if (_process is { HasExited: false })
            {
                _process.Kill(entireProcessTree: true);
            }
        }
        catch { /* 後始末なので失敗は無視 */ }
        _process?.Dispose();
        try { if (File.Exists(_dbPath)) File.Delete(_dbPath); } catch { }
        return Task.CompletedTask;
    }

    private async Task WaitUntilReadyAsync()
    {
        using var http = new HttpClient { BaseAddress = new Uri(BaseAddress) };
        for (var i = 0; i < 50; i++)
        {
            if (_process is { HasExited: true })
            {
                throw new InvalidOperationException(
                    "サーバが起動前に終了しました。uv/uvicorn は使えますか?\n" + Log());
            }
            try
            {
                var res = await http.GetAsync("/products");
                if (res.IsSuccessStatusCode)
                {
                    return;
                }
            }
            catch { /* まだ起動していない */ }
            await Task.Delay(200);
        }
        throw new TimeoutException("サーバが時間内に ready になりませんでした。\n" + Log());
    }

    private string Log()
    {
        lock (_log) { return _log.ToString(); }
    }

    private static int FreePort()
    {
        var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        var port = ((IPEndPoint)listener.LocalEndpoint).Port;
        listener.Stop();
        return port;
    }

    private static string FindRepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !File.Exists(Path.Combine(dir.FullName, "server", "pyproject.toml")))
        {
            dir = dir.Parent;
        }
        return dir?.FullName
            ?? throw new DirectoryNotFoundException("repo root(server/pyproject.toml)が見つかりません");
    }
}
