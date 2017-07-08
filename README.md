# A repository which stores Python scripts for Twitter Sentiment analysis jobs.

# Usage

## Collect tweet streams based on a perticular event/keyword. E.g:-

```
	python twitter_stream_download.py -q FakeNews -d <directory-where-tweet-streams-to-store>
```

## Evaluate sentiments based on the tweets you received. E.g:-

```
	python sentiment_evaluator <filename-where-tweet-streams-are-stored>
```

# TODOS

1. Implementation of more accurate tweet stream collection logic as per keyword and events
2. Develop logic for filtering out bad stuffs in tweet streams(hyperlink, bad mentions...)
3. Provide more flexibility for user to visualize tweet sentiments(graph, chart......)