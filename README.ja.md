# ctx-ledger

**プロジェクト説明をAIに何度も繰り返さないためのCLIツール。**

`ctx-ledger` は、ChatGPT / Codex / Claude Code / Cursor などの AI コーディングエージェントへ渡す「引き継ぎ文脈」を Markdown として自動生成します。

Git がコード変更を管理するなら、ctx-ledger は AI に渡す作業文脈を管理します。

## 何が便利か

AI と開発していると、次のような説明を何度も書きがちです。

```text
このプロジェクトは何か
今どのファイルを変更しているか
何を試したか
次に何を見てほしいか
```

`ctx-ledger` は、メモと Git 状態からこの説明をまとめて、次のチャットに貼れる `NEXT_PROMPT.md` を作ります。

## インストール

```powershell
python -m pip install "ctx-ledger @ git+https://github.com/kuto87/ctx-ledger.git"
```

開発用に clone する場合:

```powershell
git clone https://github.com/kuto87/ctx-ledger.git
cd ctx-ledger
python -m pip install -e ".[dev]"
pytest
```

## 最初に一回だけ

使いたい Git プロジェクトの中で実行します。

```powershell
ctx init
ctx config --lang ja --target chatgpt
```

## 普段使うコマンド

基本はこれだけ覚えれば大丈夫です。

```powershell
ctx handoff "今やったこと、次にAIへ頼みたいこと"
```

これは内部で次の処理をまとめて行います。

```text
ctx note
ctx snap
ctx ask
```

生成される主なファイル:

```text
.ctx-ledger/generated/NEXT_PROMPT.md
.ctx-ledger/generated/DELTA_PACK.md
.ctx-ledger/generated/RECOVERY_PACK.md
```

## コマンドを忘れたら

```powershell
ctx
```

と打つと短いガイドが出ます。

## よく使うコマンド

```powershell
ctx handoff "message"       # メモ保存 + Git状態取得 + プロンプト生成
ctx note "message"          # メモだけ保存
ctx ask                     # プロンプト生成
ctx status                  # 状態確認
ctx doctor                  # 環境チェック
ctx config --lang ja        # 日本語出力を既定にする
```

## 言語切替について

対応している出力言語は `en` と `ja` です。

これは `NEXT_PROMPT.md` などの生成文と CLI 表示の言語切替です。Python / JavaScript など、プロジェクトのプログラミング言語とは関係ありません。

## budget とは

`budget` は AI に渡す文脈サイズの目安です。

```powershell
ctx config --budget 4000
```

これは API を呼ぶものでも、課金するものでもありません。最初は無視して大丈夫です。

## デモ

短い使用例は [docs/demo.md](docs/demo.md) にあります。

## ライセンス

MIT
