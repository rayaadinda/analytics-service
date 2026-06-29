from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback

from app.models.schemas import RunClusteringRequest
from app.services.data_service import fetch_aggregated_data
from app.services.clustering_service import run_kmeans_clustering
from app.services.result_service import save_clustering_results

app = FastAPI(title="KJI Analytics Service")

# Setup CORS (allow all for local dev, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "analytics-service"}

@app.post("/api/clustering/run")
async def run_clustering(request: RunClusteringRequest, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
        
    try:
        # 1. Fetch Data
        df = fetch_aggregated_data(request.start_date, request.end_date)
        
        if len(df) == 0:
            raise HTTPException(status_code=400, detail="No transaction data found for the given period.")
            
        # 2. Run K-Means Clustering
        result = run_kmeans_clustering(df, request.n_clusters)
        
        clustered_df = result["clustered_data"]
        metrics = result["metrics"]
        
        # 3. Format Payload for Backend
        results_list = []
        for _, row in clustered_df.iterrows():
            results_list.append({
                "inventoryId": row["inventory_id"],
                "itemName": row["part_name"],
                "frekuensiTransaksi": int(row["jumlah_transaksi"]),
                "totalPenggunaan": int(row["total_qty"]),
                "jumlahHariAktif": int(row["frekuensi_hari"]),
                "jumlahWorkOrder": int(row["jumlah_wo"]),
                "clusterIndex": int(row["cluster"]),
                "clusterLabel": row["cluster_label"],
                "silhouetteScore": None  # Optional per-item score if needed
            })
            
        payload = {
            "periodeAwal": request.start_date.isoformat(),
            "periodeAkhir": request.end_date.isoformat(),
            "totalItems": len(clustered_df),
            "jumlahCluster": request.n_clusters,
            "metode": "K-Means",
            "silhouetteScore": metrics["silhouette_score"],
            "dbiScore": metrics["davies_bouldin_index"],
            "results": results_list
        }
        
        # 4. Save to Backend via API
        save_response = await save_clustering_results(payload, authorization)
        
        return {
            "success": True,
            "message": "Clustering completed and saved successfully",
            "data": save_response["data"]
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
