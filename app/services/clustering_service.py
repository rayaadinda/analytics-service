import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score

def run_kmeans_clustering(df: pd.DataFrame, n_clusters=3):
    if len(df) < n_clusters:
        raise ValueError("Not enough data points to form the requested number of clusters.")
        
    feature_cols = ['jumlah_transaksi', 'frekuensi_hari', 'total_qty', 'rata_rata_qty', 'jumlah_wo']
    X = df[feature_cols].copy()
    
    # 3. Normalisasi Data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 4. Proses K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # 5. Evaluasi Model
    sil_score = silhouette_score(X_scaled, df['cluster'])
    db_index = davies_bouldin_score(X_scaled, df['cluster'])
    
    # 6. Ringkasan Cluster
    cluster_summary = df.groupby('cluster')[feature_cols].mean().reset_index()
    
    # 7. Label Cluster
    # Label diberikan berdasarkan intensitas penggunaan tertinggi ke terendah
    cluster_order = cluster_summary.sort_values(['total_qty', 'jumlah_transaksi', 'frekuensi_hari'], ascending=False)['cluster'].tolist()
    
    # Map the ordered clusters to labels
    label_map = {}
    if n_clusters == 3:
        label_map = {
            cluster_order[0]: 'Fast Moving',
            cluster_order[1]: 'Medium Moving',
            cluster_order[2]: 'Slow Moving'
        }
    else:
        for i, c in enumerate(cluster_order):
            label_map[c] = f'Rank {i+1}'
            
    df['cluster_label'] = df['cluster'].map(label_map)
    
    return {
        "clustered_data": df,
        "metrics": {
            "silhouette_score": sil_score,
            "davies_bouldin_index": db_index
        }
    }
