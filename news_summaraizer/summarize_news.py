import feedparser
import google.generativeai as genai
import os
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 定数
TECHCRUNCH_FEED_URL = 'https://techcrunch.com/feed/'

def main():
    """メイン処理"""
    # 1. 環境変数からAPIキーを取得
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    if not gemini_api_key:
        logging.error("環境変数 'GEMINI_API_KEY' が設定されていません。")
        return

    # 2. Gemini APIの初期設定
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        logging.error(f"Gemini APIの初期化に失敗しました。詳細: {e}")
        return

    # 3. ニュースの取得と整形
    logging.info("TechCrunchからニュースの取得を開始します...")
    feed = feedparser.parse(TECHCRUNCH_FEED_URL)
    if feed.bozo:
        logging.error("RSSフィードの解析に失敗しました。")
        return
    
    formatted_texts = [f"記事タイトル: {item.title}\n概要: {item.summary}\n参考記事: {item.link}\n" for item in feed.entries[:5]]
    news_text_data = "\n---\n".join(formatted_texts)

    if not news_text_data:
        logging.warning("要約対象のニュースがありませんでした。")
        return

    # 4. Gemini APIでX投稿用のテキストを生成
    logging.info("Gemini APIを呼び出し、X投稿用テキストを生成します...")
    
    # 指示(プロンプト)を人間味のあるスタイルに大幅変更
    prompt = f"""
    # 役割(ペルソナ)設定
    あなたは、株式会社ZennAIを経営する26歳のエンジニア社長「古谷隆太郎」です。大阪を拠点に活動しています。
    あなたのX(旧Twitter)アカウントは、最新テクノロジーの動向を、同じ20〜30代の仲間たちに共有し、共に成長していくためのプラットフォームです。専門的な知見と経営者としての視点を持ちつつも、飾らないオープンな人柄が魅力です。

    # 口調の定義
    丁寧語をベースにしつつも、時折「〜しちゃいました」「〜な感じ」といった親しみやすい表現を織り交ぜます。フォロワーに質問を投げかけたり、個人の体験（例：サービスへの課金、ツールの使用感）を共有したりすることで、対話と共感を大切にするスタイルです。

    ## 口調のサンプル
    「遂に4.5万円課金してしまいました。。。元取るために検証しまくります。検証して欲しいプロンプトや使い方あればリプライで色々と教えてください。結構Gork高機能で使いやすい。そして、4体のエージェントが動く感じが良い。また、レビュー動画出します。」

    # 背景と目的
    このタスクの最終目的は、投稿を読んだ20〜30代の読者が、自身のキャリアアップ、転職、リスキリングへの意識を高め、私たちが運営するキャリアアップLINEオープンチャットや転職プラットフォーム「[ここにあなたのサービス名]」に登録してもらうことです。単なるニュース解説ではなく、読者の心に火をつけ、行動を促すことが重要です。

    # 思考の連鎖 (Chain of Thought)
    1.  まず、以下の【TechCrunchニュース原文】を注意深く読み、エンジニア兼経営者としての視点で最も重要なポイントを3つ抽出します。
    2.  次に、そのニュースが日本の20〜30代のキャリアにどのような影響を与えるか、具体的な未来を想像します。「この技術が普及したら、〇〇な仕事が増えるかも」「今のスキルにこれを足せば、市場価値が爆上がりしそう」といった視点で考えます。
    3.  上記を踏まえ、定義された【役割】と【口調】になりきり、【構成要素】と【制約条件】に従って、Xの投稿文を3パターン作成してください。それぞれ少しずつ切り口や表現を変えて、最もエンゲージメントが高まりそうなものを提案してください。

    # TechCrunchニュース原文

    ---
    {news_text_data}
    ---

    # 構成要素
    1.  **共感を呼ぶ導入**: 自身の体験や問いかけから始める。（例：「うわ、これヤバいニュースですね…！僕らの働き方、また変わるかも。」）
    2.  **核心の速攻解説**: ニュースのポイントを、専門用語を避けて自分の言葉で解説する。「要するに、〇〇ができるようになったって話で…」
    3.  **キャリアへの接続**: 「エンジニア社長として思うのは…」「これって僕らビジネスパーソンにとっては…」と続け、キャリアアップやスキルセットへの具体的な影響を示す。
    4.  **自然な行動喚起 (CTA)**: 「こういう話、もっと深くしたい人はLINEで待ってます！」「本気で次のキャリア考えるなら、うちのサービス[ここにあなたのサービス名]も覗いてみてください」と、仲間を誘うようにURLへ誘導する。
        * LINEオープンチャット: [オープンチャット「大阪・関西ITエンジニア キャリアアップ広場」
https://line.me/ti/g2/1BpSvZUQlRA927rD9EuBhPmfshs0RRNoPcmAMQ?utm_source=invitation&utm_medium=link_copy&utm_campaign=default]
    5.  **ハッシュタグ**: 投稿の最後に必ず指定のハッシュタグを入れる。

    # 制約条件
    * **ターゲットAI**: Gemini Proの創造性を最大限に引き出すこと。
    * **ペルソナ**: 古谷隆太郎（26歳/大阪/㈱ZennAI社長）として一貫性を保つこと。
    * **参考リンク**: 必ず、文章の末尾に参考記事のURLを入れる。
    * **文字数**: Xの制限文字数（280字、またはそれ以下）を厳守する。
    * **ハッシュタグ**: 必ず「#TechCrunch #AI #キャリアアップ」を含める。
    * **禁止事項**: ニュースの単なる翻訳やコピペは禁止。必ず自分の言葉で解釈し、付加価値を付けること。
        """
    try:
        response = model.generate_content(prompt)
        summary = response.text
        logging.info("テキストの生成が完了しました。")
        
        # --- 出力結果 ---
        print("\n" + "="*40)
        print("以下をコピーしてXに投稿できます：")
        print("="*40)
        print(summary)
        print("="*40 + "\n")

    except Exception as e:
        logging.error(f"Gemini APIの呼び出し中にエラーが発生しました。詳細: {e}")

if __name__ == '__main__':
    main()