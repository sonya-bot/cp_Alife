<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# ブランチの操作にかかわらず、githubに関する操作を行うコマンドを一覧でまとめてほしい

GitHubでよく使う基本的な操作コマンドを、ブランチ操作に限らず**一覧表**としてまとめます。
初期設定・リモート連携・コミット・プッシュ・履歴確認・タグ付けなど、主要なGit/GitHub操作を網羅しています[^1][^5][^6][^7]。

---

## GitHub操作コマンド 一覧

| コマンド例 | 説明 |
| :-- | :-- |
| `git config --global user.name "名前"` | ユーザー名を設定 |
| `git config --global user.email "メール"` | メールアドレスを設定 |
| `git init` | 新しいローカルリポジトリを作成 |
| `git clone <URL>` | リモートリポジトリをローカルに複製 |
| `git remote -v` | リモートリポジトリ一覧を表示 |
| `git remote add origin <URL>` | リモートリポジトリを追加 |
| `git remote remove <名前>` | リモートリポジトリを削除 |
| `git status` | 現在の状態を表示 |
| `git add <ファイル名>` | ファイルをステージに追加 |
| `git add .` | すべての変更をステージに追加 |
| `git commit -m "メッセージ"` | 変更をコミット |
| `git commit --amend -m "新しいメッセージ"` | 直前のコミットを修正 |
| `git push -u origin <ブランチ名>` | リモートリポジトリへプッシュ（初回は-u推奨） |
| `git push` | 変更をリモートに送信 |
| `git pull` | リモートの変更を取得しマージ |
| `git fetch` | リモートの最新情報を取得（マージなし） |
| `git log` | コミット履歴を表示 |
| `git log --oneline` | 1行で簡潔に履歴を表示 |
| `git diff` | 変更点を確認 |
| `git mv <旧ファイル> <新ファイル>` | ファイル名を変更・移動 |
| `git rm <ファイル名>` | ファイルを削除 |
| `git stash` | 作業内容を一時退避 |
| `git stash pop` | 一時退避した作業を復元 |
| `git tag` | タグ一覧を表示 |
| `git tag <タグ名>` | タグを作成 |
| `git tag -a <タグ名> -m "説明"` | 注釈付きタグを作成 |
| `git push origin <タグ名>` | タグをリモートにプッシュ |
| `git push origin --tags` | すべてのタグをリモートにプッシュ |
| `git branch` | ブランチ一覧を表示 |
| `git branch <ブランチ名>` | 新しいブランチを作成 |
| `git checkout <ブランチ名>` | 指定ブランチに切り替え |
| `git checkout -b <ブランチ名>` | 新しいブランチを作成し切り替え |
| `git merge <ブランチ名>` | 指定ブランチの内容を統合 |
| `git rebase <ブランチ名>` | 指定ブランチの変更を適用 |
| `git branch -d <ブランチ名>` | ローカルブランチを削除 |
| `git push origin --delete <ブランチ名>` | リモートブランチを削除 |


---

### 補足

- ほとんどの操作は**ローカル作業→コミット→プッシュ**の流れで進みます。
- `git status`や`git log`などで、常に作業状況を確認するのが安全です。
- タグやstashなどは、リリース管理や一時退避に便利です。

---

この一覧をメモやドキュメントとして保存しておくと、GitHub作業の効率が大きく向上します[^1][^5][^6]。

<div style="text-align: center">⁂</div>

[^1]: https://qiita.com/marlion01/items/ba3bac2810f8a7cc94c9

[^2]: https://zenn.dev/tmasuyama1114/articles/git-basic-commands

[^3]: https://training.github.com/downloads/ja/github-git-cheat-sheet.pdf

[^4]: https://www.kagoya.jp/howto/it-glossary/develop/howtousegithub/

[^5]: https://www.sejuku.net/blog/5816

[^6]: https://zenn.dev/lia/articles/c52d21c67bfddf

[^7]: https://ascii.jp/elem/000/004/239/4239509/2/

[^8]: https://qiita.com/trafford_777/items/b40135995de01ae95dc2

[^9]: https://ticklecode.com/gitcommandlist/

[^10]: https://docs.github.com/ja/get-started/accessibility/keyboard-shortcuts

