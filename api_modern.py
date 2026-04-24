import os
import uuid
import asyncio
import subprocess
import time
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import core

app = FastAPI(title="UVR5 Premium API")

@app.get("/models")
async def get_models():
    return {
        "roformer": list(core.roformer_models.keys()),
        "mdx23c": core.mdx23c_models,
        "mdxnet": core.mdxnet_models,
        "vrarch": core.vrarch_models,
        "demucs": core.demucs_models,
        "formats": core.output_format
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    file_path = f"uploads/{file_id}{ext}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"file_path": os.path.abspath(file_path), "filename": file.filename}

@app.post("/download")
async def download_from_link(url: str):
    try:
        file_path = core.download_audio(url)
        return {"file_path": file_path, "filename": os.path.basename(file_path)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/search")
async def search_yt(q: str, max_results: int = 5):
    try:
        results = core.search_youtube(q, max_results=max_results)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Ensure directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs(core.out_dir, exist_ok=True)

# Tasks tracking
tasks = {}

class SeparationRequest(BaseModel):
    model_type: str # "roformer", "mdx23c", "mdxnet", "vrarch", "demucs"
    model_key: str
    audio_path: str
    out_format: str = "mp3"
    params: dict = {}

def progress_callback(task_id, progress, message):
    tasks[task_id]["progress"] = progress
    tasks[task_id]["message"] = message

async def run_separation_task(task_id, request: SeparationRequest):
    try:
        cb = lambda p, m: progress_callback(task_id, p, m)
        
        if request.model_type == "roformer":
            stems = core.roformer_separator(
                request.audio_path, request.model_key, request.out_format,
                request.params.get("segment_size", 256),
                request.params.get("override_segment_size", False),
                request.params.get("overlap", 8),
                request.params.get("batch_size", 1),
                request.params.get("normalization_threshold", 0.9),
                request.params.get("amplification_threshold", 0.7),
                request.params.get("single_stem", ""),
                progress_callback=cb
            )
        elif request.model_type == "mdx23c":
            stems = core.mdxc_separator(
                request.audio_path, request.model_key, request.out_format,
                request.params.get("segment_size", 256),
                request.params.get("override_segment_size", False),
                request.params.get("overlap", 8),
                request.params.get("batch_size", 1),
                request.params.get("normalization_threshold", 0.9),
                request.params.get("amplification_threshold", 0.7),
                request.params.get("single_stem", ""),
                progress_callback=cb
            )
        elif request.model_type == "mdxnet":
            stems = core.mdxnet_separator(
                request.audio_path, request.model_key, request.out_format,
                request.params.get("hop_length", 1024),
                request.params.get("segment_size", 256),
                request.params.get("denoise", True),
                request.params.get("overlap", 0.25),
                request.params.get("batch_size", 1),
                request.params.get("normalization_threshold", 0.9),
                request.params.get("amplification_threshold", 0.7),
                request.params.get("single_stem", ""),
                progress_callback=cb
            )
        elif request.model_type == "vrarch":
            stems = core.vrarch_separator(
                request.audio_path, request.model_key, request.out_format,
                request.params.get("window_size", 512),
                request.params.get("aggression", 5),
                request.params.get("tta", True),
                request.params.get("post_process", False),
                request.params.get("post_process_threshold", 0.2),
                request.params.get("high_end_process", False),
                request.params.get("batch_size", 1),
                request.params.get("normalization_threshold", 0.9),
                request.params.get("amplification_threshold", 0.7),
                request.params.get("single_stem", ""),
                progress_callback=cb
            )
        elif request.model_type == "demucs":
            stems = core.demucs_separator(
                request.audio_path, request.model_key, request.out_format,
                request.params.get("shifts", 2),
                request.params.get("segment_size", 40),
                request.params.get("segments_enabled", True),
                request.params.get("overlap", 0.25),
                request.params.get("batch_size", 1),
                request.params.get("normalization_threshold", 0.9),
                request.params.get("amplification_threshold", 0.7),
                progress_callback=cb
            )
        else:
            raise ValueError("Invalid model type")

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["stems"] = [os.path.basename(s) for s in stems if s]
        tasks[task_id]["progress"] = 1.0
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

async def run_ensemble_task(task_id, audio_path, models: list, out_format: str):
    try:
        results_vocal = []
        results_inst = []
        
        for i, m_req in enumerate(models):
            tasks[task_id]["message"] = f"Processing Model {i+1}/{len(models)}: {m_req['model_key']}..."
            tasks[task_id]["progress"] = (i / len(models)) * 0.9
            
            # Use existing logic for each model
            cb = lambda p, m: progress_callback(task_id, (i / len(models)) * 0.9 + (p / len(models)) * 0.9, f"Model {i+1}: {m}")
            
            # Temporary internal request to reuse logic with defaults
            if m_req['model_type'] == "roformer":
                stems = core.roformer_separator(
                    audio_path, m_req['model_key'], out_format,
                    256, False, 8, 1, 0.9, 0.7, "", progress_callback=cb
                )
            elif m_req['model_type'] == "mdxnet":
                stems = core.mdxnet_separator(
                    audio_path, m_req['model_key'], out_format,
                    1024, 256, False, 0.25, 1, 0.9, 0.7, "", progress_callback=cb
                )
            elif m_req['model_type'] == "vrarch":
                stems = core.vrarch_separator(
                    audio_path, m_req['model_key'], out_format,
                    512, 10, False, False, 0.2, False, 1, 0.9, 0.7, "", progress_callback=cb
                )
            elif m_req['model_type'] == "mdx23c":
                stems = core.mdxc_separator(
                    audio_path, m_req['model_key'], out_format,
                    256, False, 8, 1, 0.9, 0.7, "", progress_callback=cb
                )
            else:
                continue
                
            if len(stems) >= 2:
                results_inst.append(stems[0])
                results_vocal.append(stems[1])

        # Merge Results
        tasks[task_id]["message"] = "Ensembling: Merging results for maximum quality..."
        tasks[task_id]["progress"] = 0.95
        
        final_vocal = f"Ensemble_Vocals_{int(time.time())}.{out_format}"
        final_inst = f"Ensemble_Instrumental_{int(time.time())}.{out_format}"
        
        # Helper to merge multiple files using FFmpeg amix
        def merge_files(files, output_name):
            if not files: return None
            out_path = os.path.join(core.out_dir, output_name)
            inputs = []
            for f in files:
                inputs.extend(["-i", f])
            
            filter_complex = f"amix=inputs={len(files)}:duration=longest"
            cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, out_path]
            subprocess.run(cmd, check=True, capture_output=True)
            return output_name

        v_out = merge_files(results_vocal, final_vocal)
        i_out = merge_files(results_inst, final_inst)
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["stems"] = [v_out, i_out]
        tasks[task_id]["progress"] = 1.0
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@app.post("/ensemble")
async def start_ensemble(request: dict, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "progress": 0, "message": "Starting Ensemble...", "model_type": "ensemble"}
    background_tasks.add_task(
        run_ensemble_task, 
        task_id, 
        request.get("audio_path"), 
        request.get("models", []), 
        request.get("out_format", "mp3")
    )
    return {"task_id": task_id}

@app.post("/separate")
async def start_separation(request: SeparationRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "progress": 0, "message": "Starting...", "model_type": request.model_type}
    background_tasks.add_task(run_separation_task, task_id, request)
    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/output/{filename}")
async def get_output(filename: str):
    file_path = os.path.join(core.out_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.get("/leaderboard")
async def get_leaderboard(filter: str = "vocals"):
    # Dev Leaderboard Verileri (Tüm Önemli Modeller Dahil)
    rankings = {
        "vocals": [
            {"model": "BS-Roformer-Viperx-1297", "score": "12.97", "speed": "1.2x", "type": "Roformer (S-Tier)"},
            {"model": "BS-Roformer-Viperx-1296", "score": "12.96", "speed": "1.2x", "type": "Roformer (S-Tier)"},
            {"model": "Mel-Roformer-Viperx-1143", "score": "11.43", "speed": "1.1x", "type": "Roformer (S-Tier)"},
            {"model": "BS-Roformer-Viperx-1053", "score": "10.53", "speed": "1.3x", "type": "Roformer (Elite)"},
            {"model": "Mel-Roformer-Karaoke-Aufr33", "score": "10.19", "speed": "1.4x", "type": "Roformer (Special)"},
            {"model": "Kim_Vocal_2", "score": "9.95", "speed": "1.6x", "type": "MDX-Net (Elite)"},
            {"model": "UVR-MDX-NET-Voc_FT", "score": "9.82", "speed": "1.5x", "type": "MDX-Net (Elite)"},
            {"model": "Kim_Vocal_1", "score": "9.65", "speed": "1.7x", "type": "MDX-Net"},
            {"model": "UVR-MDX-NET_Main_438", "score": "9.45", "speed": "1.6x", "type": "MDX-Net"},
            {"model": "BS-Roformer-De-Reverb", "score": "8.95", "speed": "1.0x", "type": "Roformer (Utility)"},
            {"model": "UVR-VR-Voc-Main", "score": "8.75", "speed": "2.3x", "type": "VR Arch"},
            {"model": "Demucs-v4-htdemucs_ft", "score": "8.20", "speed": "0.8x", "type": "Demucs v4"}
        ],
        "instrumental": [
            {"model": "UVR-MDX-NET-Inst_Main", "score": "10.24", "speed": "1.4x", "type": "MDX-Net (S-Tier)"},
            {"model": "UVR-MDX-NET-Inst_HQ_1", "score": "10.12", "speed": "1.3x", "type": "MDX-Net (S-Tier)"},
            {"model": "UVR-MDX-NET-Inst_HQ_2", "score": "9.98", "speed": "1.4x", "type": "MDX-Net (Elite)"},
            {"model": "MDX23C-8KFFT-InstVoc_HQ", "score": "9.85", "speed": "1.1x", "type": "MDX23C (Elite)"},
            {"model": "Kim_Inst", "score": "9.65", "speed": "1.8x", "type": "MDX-Net"},
            {"model": "UVR-MDX-NET-Inst_full_292", "score": "9.40", "speed": "1.5x", "type": "MDX-Net"},
            {"model": "UVR-VR-Inst-Main", "score": "8.90", "speed": "2.4x", "type": "VR Arch"},
            {"model": "Demucs-v4-htdemucs", "score": "8.45", "speed": "0.9x", "type": "Demucs v4"}
        ],
        "drums": [
            {"model": "MDX23C-DrumSep-aufr33", "score": "9.85", "speed": "1.2x", "type": "MDX23C (Elite)"},
            {"model": "UVR-MDX-NET-Drums", "score": "9.60", "speed": "1.4x", "type": "MDX-Net"},
            {"model": "Kim_Drums", "score": "9.45", "speed": "1.5x", "type": "MDX-Net"},
            {"model": "Demucs-v4-6s-Drums", "score": "9.20", "speed": "0.8x", "type": "Demucs v4"},
            {"model": "UVR-VR-Drums-Main", "score": "8.95", "speed": "2.2x", "type": "VR Arch"}
        ],
        "bass": [
            {"model": "UVR-MDX-NET-Bass", "score": "9.55", "speed": "1.4x", "type": "MDX-Net"},
            {"model": "Kim_Bass", "score": "9.30", "speed": "1.5x", "type": "MDX-Net"},
            {"model": "Demucs-v4-6s-Bass", "score": "9.15", "speed": "0.8x", "type": "Demucs v4"},
            {"model": "UVR-VR-Bass-Main", "score": "8.85", "speed": "2.2x", "type": "VR Arch"}
        ]
    }
    
    data = rankings.get(filter, [])
    
    # HTML tablosu oluştur
    html = '<table class="w-full text-left border-collapse">'
    html += '<thead class="text-slate-500 text-xs uppercase tracking-wider"><tr><th class="pb-4 px-2">Rank</th><th class="pb-4">Model Name</th><th class="pb-4">SDR Score</th><th class="pb-4 text-right">Speed</th></tr></thead>'
    html += '<tbody class="text-sm">'
    for i, item in enumerate(data):
        rank_color = "text-amber-400" if i == 0 else ("text-slate-300" if i == 1 else ("text-orange-600" if i == 2 else "text-slate-500"))
        html += f'<tr class="border-t border-slate-800/50 hover:bg-white/5 transition-colors">'
        html += f'<td class="py-4 px-2 font-black {rank_color}">#{i+1}</td>'
        html += f'<td class="py-4 font-bold text-white">{item["model"]}<br><span class="text-[10px] text-indigo-400 uppercase tracking-widest">{item["type"]}</span></td>'
        html += f'<td class="py-4"><div class="flex items-center gap-2"><span class="font-mono text-emerald-400">{item["score"]}</span>'
        if i < 3:
            html += f'<span class="text-[8px] bg-emerald-500/20 text-emerald-500 px-1 rounded">S-TIER</span>'
        elif i < 7:
            html += f'<span class="text-[8px] bg-indigo-500/20 text-indigo-400 px-1 rounded">ELITE</span>'
        html += '</div></td>'
        html += f'<td class="py-4 text-right text-slate-400 font-mono">{item["speed"]}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    
    return {"html": html}

@app.post("/remix")
async def remix_audio(request: Request):
    data = await request.json()
    vocal_path = os.path.join(core.out_dir, data.get("vocal_file"))
    inst_path = os.path.join(core.out_dir, data.get("inst_file"))
    vocal_gain = data.get("vocal_gain", 0)  # in dB
    inst_gain = data.get("inst_gain", 0)    # in dB
    
    if not os.path.exists(vocal_path) or not os.path.exists(inst_path):
        return {"status": "error", "message": "Files not found"}
        
    output_filename = f"Remix_{int(time.time())}.mp3"
    output_path = os.path.join(core.out_dir, output_filename)
    
    # FFmpeg command to mix with volume filters
    cmd = [
        "ffmpeg", "-y",
        "-i", vocal_path,
        "-i", inst_path,
        "-filter_complex", f"[0:a]volume={vocal_gain}dB[v];[1:a]volume={inst_gain}dB[i];[v][i]amix=inputs=2:duration=longest:dropout_transition=0,volume=2",
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return {"status": "success", "filename": output_filename}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Serve static files (Frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
