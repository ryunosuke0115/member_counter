import sys
import os
import readchar

# --- ファイルパス設定 ---
NAMES_FILE = "names.txt"
RESULTS_FILE = "results.txt"


# 1. カンマ区切りファイルから名前を読み込む関数
def load_names_from_file(filepath):
    """
    指定されたファイルパスからカンマ区切りで名前を読み込み、
    名前をキー、カウントを値（初期値0）とする辞書を返します。
    (results.txtが見つからない場合の初期化に使用)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print(f"エラー: ファイル '{filepath}' が空です。")
                return {}

            names = [name.strip() for name in content.split(',') if name.strip()]
            counter = {name: 0 for name in names}
            return counter

    except FileNotFoundError:
        print(f"エラー: ファイル '{filepath}' が見つかりません。")
        return None
    except Exception as e:
        print(f"ファイル読み込み中にエラーが発生しました: {e}")
        return None

# 2. 過去のカウント結果を読み込む関数
def load_results_from_file(filepath):
    """
    前回終了時の結果ファイルから「名前: カウント数」を読み込み、辞書を返します。
    """
    counter = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # 「名前: カウント数」の形式を想定
                if ':' in line:
                    # 最初のコロンで分割
                    name, count_str = line.split(':', 1)
                    name = name.strip()
                    count_str = count_str.strip()

                    try:
                        count = int(count_str)
                        if name:
                            counter[name] = count
                    except ValueError:
                        print(f"警告: '{filepath}' の不正なカウント値 '{count_str}' をスキップしました。")

        if counter:
            return counter
        else:
            # ファイルは存在したが、有効なデータがなかった場合
            print(f"警告: '{filepath}' は存在しますが、有効なカウントデータが見つかりませんでした。")
            return None

    except FileNotFoundError:
        # ファイルが存在しない場合はNoneを返し、names.txtからの読み込みにフォールバックさせる
        return None
    except Exception as e:
        print(f"🚨 '{filepath}' 読み込み中に予期せぬエラーが発生しました: {e}")
        return None


# 3. ターミナル表示をクリアする関数
def clear_screen():
    """ターミナル画面をクリアします。"""
    os.system('cls' if os.name == 'nt' else 'clear')


# 4. カウント結果をファイルに保存する関数
def save_results(counter, output_filepath=RESULTS_FILE):
    """
    カウンターの最終結果をファイルに書き出します。
    """
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            print(f"\n✅ 結果をファイル '{output_filepath}' に保存しています...")
            for name, count in counter.items():
                line = f"{name}: {count}\n"
                f.write(line)
                print(f"   - {line.strip()}")
        print("💾 保存が完了しました。")
    except Exception as e:
        print(f"🚨 結果の保存中にエラーが発生しました: {e}")

# 4.5. 終了時に保存を確認する関数
def confirm_and_save(counter):
    """
    ユーザーに結果を保存するか確認し、'y' の場合に保存を実行します。
    """
    # 画面下部にプロンプトを表示するため、クリアはしない
    print("\n❓ カウント結果を保存しますか？ (y/n) [Enter] >> ", end="", flush=True)

    # 標準のinput()を使い、ユーザーがEnterを押すのを待つ
    try:
        user_input = input().strip().lower()
    except:
        user_input = 'n' # 入力エラー時は保存しない

    if user_input == 'n':
        print("💾 結果の保存をスキップしました。")
    else:
        save_results(counter)

# 5. カウンターを管理・表示するメイン関数
def run_counter(counter):
    """
    名前とカウントをターミナルに表示し、キーイベントで操作します。
    特殊キーは文字コードで直接比較します。
    """
    if not counter:
        return

    name_list = list(counter.keys())
    current_index = 0

    # 初回描画
    clear_screen()

    while True:
        # 画面描画ロジック
        clear_screen()
        print("👤 名前カウンター (TUIモード) 🔄")
        print("------------------------------")
        print("操作: [Enter] カウントアップ | [d] カウントダウン | [r] 全リセット | [↑/↓] 移動 | [q] 終了 (結果保存) | [Ctrl+C]  終了 (結果保存しない)")
        print("-" * 30)

        for i, name in enumerate(name_list):
            count = counter[name]
            prefix = ">>" if i == current_index else "  "

            print(f"{prefix} {name:<15} : {count:3}")

        print("-" * 30)

        # ユーザー入力を即座に受け付ける
        try:
            key = readchar.readkey()

        except KeyboardInterrupt:
            confirm_and_save(counter)
            break

        # q または CTRL_C ('\x03') で終了し、結果を保存する
        if key == 'q' or key == '\x03':
            confirm_and_save(counter)
            print("\n👋 カウンターを終了します。")
            break

        # Enter ('\r' または '\n') でカウントアップ
        elif key == '\r' or key == '\n':
            selected_name = name_list[current_index]
            counter[selected_name] += 1

        # d でカウントダウン
        elif key == 'd':
            selected_name = name_list[current_index]
            counter[selected_name] -= 1

        # r で全リセット
        elif key == 'r':
            for name in counter:
                counter[name] = 0
            print("❗ すべてのカウントをリセットしました。")
            readchar.readkey()

        # ↑ ('\x1b[A') で上へ移動
        elif key == '\x1b[A':
            current_index = (current_index - 1) % len(name_list)

        # ↓ ('\x1b[B') で下へ移動
        elif key == '\x1b[B':
            current_index = (current_index + 1) % len(name_list)

# 6. メイン処理
if __name__ == "__main__":

    # 1. results.txt から前回の状態を読み込もうと試みる
    name_counter = load_results_from_file(RESULTS_FILE)

    if name_counter is not None:
        print(f"✨ 既存の '{RESULTS_FILE}' から前回のカウント状態を読み込みました。")
    else:
        # 2. 読み込めなかった場合は、names.txt から新規に名前を読み込む
        print(f"⚠️ 既存の '{RESULTS_FILE}' が見つからないか、読み込めませんでした。'{NAMES_FILE}' から初期化します。")
        name_counter = load_names_from_file(NAMES_FILE)

    # 3. カウンターを実行
    if name_counter is not None and name_counter:
        run_counter(name_counter)
    else:
        print("\n❌ カウンターを開始するための有効な名前データがありません。")
