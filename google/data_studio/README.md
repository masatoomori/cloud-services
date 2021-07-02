## Geocoding
### 緯度経度
緯度を表す小数と経度を表す小数をカンマで繋ぐ
```python
df['lat_lng'] = None
df.loc[df['latitude'].notnull() & df['longitude'].notnull(), 'lat_lng'] = df[['latitude', 'longitude']].astype(str).apply(lambda row: ','.json(row), axis=1)
```