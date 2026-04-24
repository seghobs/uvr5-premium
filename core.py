import os
import sys
import subprocess
import re
import platform
import json
import copy
import urllib.parse
import torch
import logging
import yt_dlp
from audio_separator.separator import Separator

# Inject bundled ffmpeg into PATH if system ffmpeg is missing
try:
    import imageio_ffmpeg
    _ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
    if _ffmpeg_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
except Exception:
    pass

now_dir = os.getcwd()
sys.path.append(now_dir)
config_file = os.path.join(now_dir, "assets", "config.json")
models_file = os.path.join(now_dir, "assets", "models.json")
default_settings_file = os.path.join(now_dir, "assets", "default_settings.json")
custom_settings_file = os.path.join(now_dir, "assets", "custom_settings.json")

device = "cuda" if torch.cuda.is_available() else "cpu"
use_autocast = device == "cuda"

if os.path.isdir("env"):
    if platform.system() == "Windows":
        python_location = ".\\env\\python.exe"
        separator_location = ".\\env\\Scripts\\audio-separator.exe"
    elif platform.system() == "Linux":
        python_location = "env/bin/python"
        separator_location = "env/bin/audio-separator"
else:
    python_location = None
    separator_location = "audio-separator"

out_dir = "./outputs"
models_dir = "./models"
extensions = (".wav", ".flac", ".mp3", ".ogg", ".opus", ".m4a", ".aiff", ".ac3")

#=========================#
#     Model Definitions   #
#=========================#
# (Loaded from app.py logic)
roformer_models = {
    'BS-Roformer-Viperx-1297': 'model_bs_roformer_ep_317_sdr_12.9755.ckpt',
    'BS-Roformer-Viperx-1296': 'model_bs_roformer_ep_368_sdr_12.9628.ckpt',
    'BS-Roformer-Viperx-1053': 'model_bs_roformer_ep_937_sdr_10.5309.ckpt',
    'Mel-Roformer-Viperx-1143': 'model_mel_band_roformer_ep_3005_sdr_11.4360.ckpt',
    'BS-Roformer-De-Reverb': 'deverb_bs_roformer_8_384dim_10depth.ckpt',
    'Mel-Roformer-Crowd-Aufr33-Viperx': 'mel_band_roformer_crowd_aufr33_viperx_sdr_8.7144.ckpt',
    'Mel-Roformer-Denoise-Aufr33': 'denoise_mel_band_roformer_aufr33_sdr_27.9959.ckpt',
    'Mel-Roformer-Denoise-Aufr33-Aggr' : 'denoise_mel_band_roformer_aufr33_aggr_sdr_27.9768.ckpt',
    'MelBand Roformer | Denoise-Debleed by Gabox' : 'mel_band_roformer_denoise_debleed_gabox.ckpt',
    'Mel-Roformer-Karaoke-Aufr33-Viperx': 'mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt',
    'MelBand Roformer | Karaoke by Gabox' : 'mel_band_roformer_karaoke_gabox.ckpt',
    'MelBand Roformer | Karaoke by becruily' : 'mel_band_roformer_karaoke_becruily.ckpt',
    'MelBand Roformer | Vocals by Kimberley Jensen' : 'vocals_mel_band_roformer.ckpt',
    'MelBand Roformer Kim | FT by unwa' : 'mel_band_roformer_kim_ft_unwa.ckpt',
    'MelBand Roformer Kim | FT 2 by unwa' : 'mel_band_roformer_kim_ft2_unwa.ckpt',
    'MelBand Roformer Kim | FT 2 Bleedless by unwa' : 'mel_band_roformer_kim_ft2_bleedless_unwa.ckpt',
    'MelBand Roformer Kim | FT 3 by unwa' : 'mel_band_roformer_kim_ft3_unwa.ckpt',
    'MelBand Roformer Kim | Inst V1 by Unwa' : 'melband_roformer_inst_v1.ckpt',
    'MelBand Roformer Kim | Inst V1 Plus by Unwa' : 'melband_roformer_inst_v1_plus.ckpt',
    'MelBand Roformer Kim | Inst V1 (E) by Unwa' : 'melband_roformer_inst_v1e.ckpt',
    'MelBand Roformer Kim | Inst V1 (E) Plus by Unwa' : 'melband_roformer_inst_v1e_plus.ckpt',
    'MelBand Roformer Kim | Inst V2 by Unwa' : 'melband_roformer_inst_v2.ckpt',
    'MelBand Roformer Kim | InstVoc Duality V1 by Unwa' : 'melband_roformer_instvoc_duality_v1.ckpt',
    'MelBand Roformer Kim | InstVoc Duality V2 by Unwa' : 'melband_roformer_instvox_duality_v2.ckpt',
    'MelBand Roformer | Vocals by becruily' : 'mel_band_roformer_vocals_becruily.ckpt',
    'MelBand Roformer | Instrumental by becruily' : 'mel_band_roformer_instrumental_becruily.ckpt',
    'MelBand Roformer | Vocals Fullness by Aname' : 'mel_band_roformer_vocal_fullness_aname.ckpt',
    'BS Roformer | Vocals by Gabox' : 'bs_roformer_vocals_gabox.ckpt',
    'MelBand Roformer | Vocals by Gabox' : 'mel_band_roformer_vocals_gabox.ckpt',
    'MelBand Roformer | Vocals FV1 by Gabox' : 'mel_band_roformer_vocals_fv1_gabox.ckpt',
    'MelBand Roformer | Vocals FV2 by Gabox' : 'mel_band_roformer_vocals_fv2_gabox.ckpt',
    'MelBand Roformer | Vocals FV3 by Gabox' : 'mel_band_roformer_vocals_fv3_gabox.ckpt',
    'MelBand Roformer | Vocals FV4 by Gabox' : 'mel_band_roformer_vocals_fv4_gabox.ckpt',
    'MelBand Roformer | Instrumental by Gabox' : 'mel_band_roformer_instrumental_gabox.ckpt',
    'MelBand Roformer | Instrumental 2 by Gabox' : 'mel_band_roformer_instrumental_2_gabox.ckpt',
    'MelBand Roformer | Instrumental 3 by Gabox' : 'mel_band_roformer_instrumental_3_gabox.ckpt',
    'MelBand Roformer | Instrumental Bleedless V1 by Gabox' : 'mel_band_roformer_instrumental_bleedless_v1_gabox.ckpt',
    'MelBand Roformer | Instrumental Bleedless V2 by Gabox' : 'mel_band_roformer_instrumental_bleedless_v2_gabox.ckpt',
    'MelBand Roformer | Instrumental Bleedless V3 by Gabox' : 'mel_band_roformer_instrumental_bleedless_v3_gabox.ckpt',
    'MelBand Roformer | Instrumental Fullness V1 by Gabox' : 'mel_band_roformer_instrumental_fullness_v1_gabox.ckpt',
    'MelBand Roformer | Instrumental Fullness V2 by Gabox' : 'mel_band_roformer_instrumental_fullness_v2_gabox.ckpt',
    'MelBand Roformer | Instrumental Fullness V3 by Gabox' : 'mel_band_roformer_instrumental_fullness_v3_gabox.ckpt',
    'MelBand Roformer | Instrumental Fullness Noisy V4 by Gabox' : 'mel_band_roformer_instrumental_fullness_noise_v4_gabox.ckpt',
    'MelBand Roformer | INSTV5 by Gabox' : 'mel_band_roformer_instrumental_instv5_gabox.ckpt',
    'MelBand Roformer | INSTV5N by Gabox' : 'mel_band_roformer_instrumental_instv5n_gabox.ckpt',
    'MelBand Roformer | INSTV6 by Gabox' : 'mel_band_roformer_instrumental_instv6_gabox.ckpt',
    'MelBand Roformer | INSTV6N by Gabox' : 'mel_band_roformer_instrumental_instv6n_gabox.ckpt',
    'MelBand Roformer | INSTV7 by Gabox' : 'mel_band_roformer_instrumental_instv7_gabox.ckpt',
    'MelBand Roformer | INSTV7N by Gabox' : 'mel_band_roformer_instrumental_instv7n_gabox.ckpt',
    'MelBand Roformer | INSTV8 by Gabox' : 'mel_band_roformer_instrumental_instv8_gabox.ckpt',
    'MelBand Roformer | INSTV8N by Gabox' : 'mel_band_roformer_instrumental_instv8n_gabox.ckpt',
    'MelBand Roformer | FVX by Gabox' : 'mel_band_roformer_instrumental_fvx_gabox.ckpt',
    'MelBand Roformer | De-Reverb by anvuew' : 'dereverb_mel_band_roformer_anvuew_sdr_19.1729.ckpt',
    'MelBand Roformer | De-Reverb Less Aggressive by anvuew' : 'dereverb_mel_band_roformer_less_aggressive_anvuew_sdr_18.8050.ckpt',
    'MelBand Roformer | De-Reverb Mono by anvuew' : 'dereverb_mel_band_roformer_mono_anvuew.ckpt',
    'MelBand Roformer | De-Reverb Big by Sucial' : 'dereverb_big_mbr_ep_362.ckpt',
    'MelBand Roformer | De-Reverb Super Big by Sucial' : 'dereverb_super_big_mbr_ep_346.ckpt',
    'MelBand Roformer | De-Reverb-Echo by Sucial' : 'dereverb-echo_mel_band_roformer_sdr_10.0169.ckpt',
    'MelBand Roformer | De-Reverb-Echo V2 by Sucial' : 'dereverb-echo_mel_band_roformer_sdr_13.4843_v2.ckpt',
    'MelBand Roformer | De-Reverb-Echo Fused by Sucial' : 'dereverb_echo_mbr_fused.ckpt',
    'MelBand Roformer Kim | SYHFT by SYH99999' : 'MelBandRoformerSYHFT.ckpt',
    'MelBand Roformer Kim | SYHFT V2 by SYH99999' : 'MelBandRoformerSYHFTV2.ckpt',
    'MelBand Roformer Kim | SYHFT V2.5 by SYH99999' : 'MelBandRoformerSYHFTV2.5.ckpt',
    'MelBand Roformer Kim | SYHFT V3 by SYH99999' : 'MelBandRoformerSYHFTV3Epsilon.ckpt',
    'MelBand Roformer Kim | Big SYHFT V1 by SYH99999' : 'MelBandRoformerBigSYHFTV1.ckpt',
    'MelBand Roformer Kim | Big Beta 4 FT by unwa' : 'melband_roformer_big_beta4.ckpt',
    'MelBand Roformer Kim | Big Beta 5e FT by unwa' : 'melband_roformer_big_beta5e.ckpt',
    'MelBand Roformer | Big Beta 6 by unwa' : 'melband_roformer_big_beta6.ckpt',
    'MelBand Roformer | Big Beta 6X by unwa' : 'melband_roformer_big_beta6x.ckpt',
    'BS Roformer | Chorus Male-Female by Sucial' : 'model_chorus_bs_roformer_ep_267_sdr_24.1275.ckpt',
    'BS Roformer | Male-Female by aufr33' : 'bs_roformer_male_female_by_aufr33_sdr_7.2889.ckpt',
    'MelBand Roformer | Aspiration by Sucial' : 'aspiration_mel_band_roformer_sdr_18.9845.ckpt',
    'MelBand Roformer | Aspiration Less Aggressive by Sucial' : 'aspiration_mel_band_roformer_less_aggr_sdr_18.1201.ckpt',
    'MelBand Roformer | Bleed Suppressor V1 by unwa-97chris' : 'mel_band_roformer_bleed_suppressor_v1.ckpt'
}

mdx23c_models = [
    'MDX23C_D1581.ckpt',
    'MDX23C-8KFFT-InstVoc_HQ.ckpt',
    'MDX23C-8KFFT-InstVoc_HQ_2.ckpt',
    'MDX23C-De-Reverb-aufr33-jarredou.ckpt',
    'MDX23C-DrumSep-aufr33-jarredou.ckpt'
]

mdxnet_models = [
    'UVR-MDX-NET-Inst_full_292.onnx',
    'UVR-MDX-NET_Inst_187_beta.onnx',
    'UVR-MDX-NET_Inst_82_beta.onnx',
    'UVR-MDX-NET_Inst_90_beta.onnx',
    'UVR-MDX-NET_Main_340.onnx',
    'UVR-MDX-NET_Main_390.onnx',
    'UVR-MDX-NET_Main_406.onnx',
    'UVR-MDX-NET_Main_427.onnx',
    'UVR-MDX-NET_Main_438.onnx',
    'UVR-MDX-NET-Inst_HQ_1.onnx',
    'UVR-MDX-NET-Inst_HQ_2.onnx',
    'UVR-MDX-NET-Inst_HQ_3.onnx',
    'UVR-MDX-NET-Inst_HQ_4.onnx',
    'UVR-MDX-NET-Inst_HQ_5.onnx',
    'UVR_MDXNET_Main.onnx',
    'UVR-MDX-NET-Inst_Main.onnx',
    'UVR_MDXNET_1_9703.onnx',
    'UVR_MDXNET_2_9682.onnx',
    'UVR_MDXNET_3_9662.onnx',
    'UVR-MDX-NET-Inst_1.onnx',
    'UVR-MDX-NET-Inst_2.onnx',
    'UVR-MDX-NET-Inst_3.onnx',
    'UVR_MDXNET_KARA.onnx',
    'UVR_MDXNET_KARA_2.onnx',
    'UVR_MDXNET_9482.onnx',
    'UVR-MDX-NET-Voc_FT.onnx',
    'Kim_Vocal_1.onnx',
    'Kim_Vocal_2.onnx',
    'Kim_Inst.onnx',
    'Reverb_HQ_By_FoxJoy.onnx',
    'UVR-MDX-NET_Crowd_HQ_1.onnx',
    'kuielab_a_vocals.onnx',
    'kuielab_a_other.onnx',
    'kuielab_a_bass.onnx',
    'kuielab_a_drums.onnx',
    'kuielab_b_vocals.onnx',
    'kuielab_b_other.onnx',
    'kuielab_b_bass.onnx',
    'kuielab_b_drums.onnx',
]

vrarch_models = [
    '1_HP-UVR.pth',
    '2_HP-UVR.pth',
    '3_HP-Vocal-UVR.pth',
    '4_HP-Vocal-UVR.pth',
    '5_HP-Karaoke-UVR.pth',
    '6_HP-Karaoke-UVR.pth',
    '7_HP2-UVR.pth',
    '8_HP2-UVR.pth',
    '9_HP2-UVR.pth',
    '10_SP-UVR-2B-32000-1.pth',
    '11_SP-UVR-2B-32000-2.pth',
    '12_SP-UVR-3B-44100.pth',
    '13_SP-UVR-4B-44100-1.pth',
    '14_SP-UVR-4B-44100-2.pth',
    '15_SP-UVR-MID-44100-1.pth',
    '16_SP-UVR-MID-44100-2.pth',
    '17_HP-Wind_Inst-UVR.pth',
    'UVR-De-Echo-Aggressive.pth',
    'UVR-De-Echo-Normal.pth',
    'UVR-DeEcho-DeReverb.pth',
    'UVR-De-Reverb-aufr33-jarredou.pth',
    'UVR-DeNoise-Lite.pth',
    'UVR-DeNoise.pth',
    'UVR-BVE-4B_SN-44100-1.pth',
    'MGM_HIGHEND_v4.pth',
    'MGM_LOWEND_A_v4.pth',
    'MGM_LOWEND_B_v4.pth',
    'MGM_MAIN_v4.pth',
]

demucs_models = [
    'htdemucs_ft.yaml',
    'htdemucs_6s.yaml',
    'htdemucs.yaml',
    'hdemucs_mmi.yaml',
]

output_format = ['wav', 'flac', 'mp3', 'ogg', 'opus', 'm4a', 'aiff', 'ac3']

#=========================#
#     Core Functions      #
#=========================#

def download_audio(url, output_dir="ytdl"):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '32',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessor_args': ['-acodec', 'pcm_f32le'],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info['title']
            ydl.download([url])
            file_path = os.path.join(output_dir, f"{video_title}.wav")
            if os.path.exists(file_path):
                return os.path.abspath(file_path)
            else:
                raise Exception("Something went wrong")
    except Exception as e:
        raise Exception(f"Error extracting audio with yt-dlp: {str(e)}")

def search_youtube(query, max_results=5):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{max_results}:{query}"
            info = ydl.extract_info(search_query, download=False)
            results = []
            if 'entries' in info:
                for entry in info['entries']:
                    results.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'duration': entry.get('duration'),
                        'thumbnail': f"https://i.ytimg.com/vi/{entry.get('id')}/hqdefault.jpg"
                    })
            return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

def leaderboard(list_filter):
    try:
        command = [python_location if python_location else "python", separator_location, "-l", f"--list_filter={list_filter}"]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return "<table border='1'>" + "".join(
            f"<tr style='{'font-weight: bold; font-size: 1.2em;' if i == 0 else ''}'>" +
            "".join(f"<td>{cell}</td>" for cell in re.split(r"\s{2,}", line.strip())) +
            "</tr>"
            for i, line in enumerate(re.findall(r"^(?!-+)(.+)$", result.stdout.strip(), re.MULTILINE))
        ) + "</table>"
    except Exception as e:
        return f"Error: {e}"

def generic_separator(audio, model_filename, params, progress_callback=None):
    try:
        separator = Separator(
            log_level=logging.WARNING,
            model_file_dir=models_dir,
            output_dir=out_dir,
            use_autocast=use_autocast,
            **params
        )
        if progress_callback: progress_callback(0.2, "Loading model...")
        separator.load_model(model_filename=model_filename)
        if progress_callback: progress_callback(0.7, "Separating audio...")
        separation = separator.separate(audio)
        stems = [os.path.join(out_dir, file_name) for file_name in separation]
        return stems
    except Exception as e:
        raise RuntimeError(f"Separation failed: {e}") from e

def roformer_separator(audio, model_key, out_format, segment_size, override_seg_size, overlap, batch_size, norm_thresh, amp_thresh, single_stem, progress_callback=None):
    model_filename = roformer_models[model_key]
    params = {
        "output_format": out_format,
        "normalization_threshold": norm_thresh,
        "amplification_threshold": amp_thresh,
        "output_single_stem": single_stem,
        "mdxc_params": {
            "segment_size": segment_size,
            "override_model_segment_size": override_seg_size,
            "batch_size": batch_size,
            "overlap": overlap,
        }
    }
    return generic_separator(audio, model_filename, params, progress_callback)

def mdxc_separator(audio, model, out_format, segment_size, override_seg_size, overlap, batch_size, norm_thresh, amp_thresh, single_stem, progress_callback=None):
    params = {
        "output_format": out_format,
        "normalization_threshold": norm_thresh,
        "amplification_threshold": amp_thresh,
        "output_single_stem": single_stem,
        "mdxc_params": {
            "segment_size": segment_size,
            "override_model_segment_size": override_seg_size,
            "batch_size": batch_size,
            "overlap": overlap,
        }
    }
    return generic_separator(audio, model, params, progress_callback)

def mdxnet_separator(audio, model, out_format, hop_length, segment_size, denoise, overlap, batch_size, norm_thresh, amp_thresh, single_stem, progress_callback=None):
    params = {
        "output_format": out_format,
        "normalization_threshold": norm_thresh,
        "amplification_threshold": amp_thresh,
        "output_single_stem": single_stem,
        "mdx_params": {
            "hop_length": hop_length,
            "segment_size": segment_size,
            "overlap": overlap,
            "batch_size": batch_size,
            "enable_denoise": denoise,
        }
    }
    return generic_separator(audio, model, params, progress_callback)

def vrarch_separator(audio, model, out_format, window_size, aggression, tta, post_process, post_process_threshold, high_end_process, batch_size, norm_thresh, amp_thresh, single_stem, progress_callback=None):
    params = {
        "output_format": out_format,
        "normalization_threshold": norm_thresh,
        "amplification_threshold": amp_thresh,
        "output_single_stem": single_stem,
        "vr_params": {
            "batch_size": batch_size,
            "window_size": window_size,
            "aggression": aggression,
            "enable_tta": tta,
            "enable_post_process": post_process,
            "post_process_threshold": post_process_threshold,
            "high_end_process": high_end_process,
        }
    }
    return generic_separator(audio, model, params, progress_callback)

def demucs_separator(audio, model, out_format, shifts, segment_size, segments_enabled, overlap, batch_size, norm_thresh, amp_thresh, progress_callback=None):
    params = {
        "output_format": out_format,
        "normalization_threshold": norm_thresh,
        "amplification_threshold": amp_thresh,
        "demucs_params": {
            "batch_size": batch_size,
            "segment_size": segment_size,
            "shifts": shifts,
            "overlap": overlap,
            "segments_enabled": segments_enabled,
        }
    }
    return generic_separator(audio, model, params, progress_callback)
