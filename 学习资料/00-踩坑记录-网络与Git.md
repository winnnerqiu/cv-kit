# 踩坑记录：网络与 Git（W1 期间）

> 记录时间：2026-09-22
> 场景：第一次把 `~/cv-kit` 推送到 GitHub

## 现象

```bash
$ git push -u origin main
fatal: unable to access 'https://github.com/winnnerqiu/cv-kit.git/':
Failed to connect to github.com port 443 after 3 ms: Connection refused
```

## 排查过程（有用的思路）

| 步骤 | 命令 | 发现 |
| --- | --- | --- |
| 1 | `getent hosts github.com` | **返回 `127.0.0.1`** ← 关键线索：域名被解析到本机 |
| 2 | `cat /etc/hosts` | WSL 的 hosts 干净，没问题 |
| 3 | `grep -i github /mnt/c/Windows/System32/drivers/etc/hosts` | **Windows hosts 里有 27 条** `127.0.0.1 xxx.github.com` 记录（含 `api.github.com`） |
| 4 | `curl --resolve github.com:443:140.82.112.3 https://github.com` | **HTTP 200** → 网络本身通，问题 100% 在 DNS |
| 5 | 用公共 DNS 对比（8.8.8.8 / 114.114.114.114） | 都返回真实地址 `20.205.243.166` |

## 根因

**Windows 的 hosts 文件被写入了 27 条 GitHub 屏蔽记录**，把 `github.com`、`api.github.com` 等
全部指向 `127.0.0.1`（本机），任何连接都会立刻被拒绝。
WSL 的 DNS 解析会走 Windows 侧，所以 WSL 里也一并被污染。

（写入来源不明，疑似某次"修复 GitHub 访问"的教程或工具留下的规则。文件时间戳 2026-09-22 17:22。）

## 最终解法（有效）

**不折腾 Windows hosts，直接在 WSL 里覆盖解析结果**：

```bash
sudo sh -c 'cp /etc/hosts /etc/hosts.bak && printf "\n# GitHub 真实地址\n140.82.112.3\tgithub.com\n20.205.243.166\tapi.github.com\n140.82.112.3\tcodeload.github.com\n" >> /etc/hosts'
```

原理：`/etc/nsswitch.conf` 里 `hosts: files dns` —— **files（/etc/hosts）优先于 dns**，
所以在 WSL 里写死真实 IP，就能盖住上游的污染。

### 真实 IP 从哪来

```bash
# 问公共 DNS（不受本机 hosts 影响）
nslookup github.com 8.8.8.8          # → 20.205.243.166
# 或逐个测连通性
for ip in 140.82.112.3 140.82.113.3 140.82.114.3 20.205.243.166; do
  timeout 6 bash -c "echo > /dev/tcp/$ip/443" && echo "$ip 通" || echo "$ip 不通"
done
```

本次实测可用：`140.82.112.3`、`140.82.113.3`、`140.82.114.3`、`20.205.243.166`

## 附带修复：Git 凭据管理器路径的空格问题

### 现象

```bash
fatal: could not read Username for 'https://github.com'
/mnt/c/Program Files/Git/mingw64/bin/git-credential-manager.exe get: 1: /mnt/c/Program: not found
```

### 原因

之前配置时用的命令：

```bash
git config --global credential.helper "/mnt/c/Program Files/.../git-credential-manager.exe"
```

shell 把双引号**吃掉了**，git 配置里存的是**带空格的裸路径**；git 再把它交给 shell 执行时，
`/mnt/c/Program` 被当成命令名 → 找不到。

### 正确写法（实测有效）

```bash
git config --global credential.helper "/mnt/c/Program\ Files/Git/mingw64/bin/git-credential-manager.exe"
```

即：**配置值里的空格要用反斜杠转义**，而不是用引号包住整个值。

（另一种错误写法：把引号也写进配置值 `credential.helper="\"/mnt/c/...\""`，
git 会把它当成叫 `credential-/mnt/c/...` 的子命令 → 报 `is not a git command`。）

## 待观察

- Windows hosts 里那 27 条记录**还在**（本次没清掉，因为需要管理员权限且脚本未成功执行）。
  目前靠 WSL 侧 `/etc/hosts` 覆盖绕过，**WSL 里 git 可以正常用**。
- 如果将来发现解析又变回 `127.0.0.1`，检查是不是某个工具（如 Clash Verge 的 hosts 模式）
  在自动重写 hosts 文件。
- 如果以后需要关掉 Clash Verge 的 hosts 自动改写，或彻底清 Windows hosts，
  记得**先备份**：`copy hosts hosts.bak`。

## 复现检查清单（下次遇到"连不上 GitHub"）

1. `getent hosts github.com` —— 是不是 `127.0.0.1`？
2. `grep -i github /mnt/c/Windows/System32/drivers/etc/hosts` —— Windows hosts 有没有脏记录？
3. `curl --resolve github.com:443:140.82.112.3 https://github.com` —— 绕过 DNS 能不能通？
4. `git config --global --get credential.helper` —— 路径里的空格转义了吗？
5. `printf "protocol=https\nhost=github.com\n" | git credential fill` —— 凭据还在不在？
