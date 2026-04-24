<h1 align="center"><b> 🎵 UVR5 Premium 🎵 </b></h1>
<div align="center">

[![madewithlove](https://img.shields.io/badge/made_with-%E2%9D%A4-red?style=for-the-badge&labelColor=orange)](https://github.com/seghobs/uvr5-premium)

### **The Most Advanced Audio Separation Dashboard**
*Powered by FastAPI, Alpine.js, and Modern AI Models*

</div>

---

## 🚀 UVR5 Premium Enhancements

We have completely overhauled the original UVR5-UI to provide a **Premium, High-Performance experience**.

### **✨ Key Features:**
*   **💎 Premium Glassmorphism UI:** A stunning, modern dashboard with cubic-bezier animations, dark mode, and responsive layout.
*   **🔍 Integrated YouTube Search:** Search for any video directly within the app and add it to your processing queue instantly.
*   **⚡ High-Performance FastAPI Backend:** Replaced legacy Gradio with a lightning-fast asynchronous API for better stability and lower latency.
*   **🎚️ Studio Remix & Merge:** A professional-grade mixing panel with real-time gain control (dB), Web Audio API previewing, and high-fidelity export.
*   **📈 Model Performance Leaderboard:** Real-time S-Tier and Elite model rankings based on SDR (Signal-to-Distortion) scores.
*   **🔄 Infinite Scroll Discovery:** Browse YouTube results and your library with a seamless infinite loading experience.
*   **🧠 Intelligent Ensemble Mode:** Combine multiple S-Tier models (Roformer + MDX-Net) for the ultimate separation quality.
*   **🛠️ Optimized Processing:** Improved z-index management, batch processing with progress tracking, and error handling.

## 🛠️ Requirements & Installation

### Hardware:
*   **GPU:** NVIDIA RTX 2000 Series or higher (Highly Recommended).
*   **RAM:** 16GB+ for best performance with large models.

### Installation:
1.  **Clone:** `git clone https://github.com/seghobs/uvr5-premium.git`
2.  **Install:** Run `UVR5-UI-installer.bat`.
3.  **Launch:** Run `run_modern.bat` to start the Premium Dashboard.

---

## 🏗️ Core Separation Engine
UVR5 Premium supports the industry's most advanced architectures:
*   **BS/Mel-Roformer:** The gold standard for vocal and instrumental separation.
*   **MDX23C:** Cutting-edge architectures for high-fidelity stem extraction.
*   **MDX-NET:** The classic, robust engine for all-around performance.
*   **VR Arch / Demucs v4:** Specialized models for drums, bass, and complex mixes.

## Requirements

### Hardware Requirements:
* Nvidia Series 2000 (RTX) or higher.
* At least 10Gb of disk space. 

> [!NOTE]  
> Older NVIDIA GPUs will be very slow. CPU will be insanely slow. If you don't meet the hardware requirements use our [Colab](https://colab.research.google.com/github/Eddycrack864/UVR5-UI/blob/main/UVR_UI.ipynb)/[Kaggle](https://www.kaggle.com/code/eddycrack864/uvr5-ui)/[Lightning.ai](https://lightning.ai/eddycrack864/studios/uvr5-ui)/[Hugging Face](https://huggingface.co/spaces/TheStinger/UVR5_UI).

### Prerequisites:
- Git. You can download Git [here](https://git-scm.com/downloads).
- FFmpeg. You can download FFmpeg [here](https://www.ffmpeg.org/download.html) or you can use my [automated installation script](https://github.com/Eddycrack864/UVR5-UI/blob/main/info/ffmpeg-installer.bat) (for Windows).
- For linux users, run this command on an terminal: (Debian and Ubuntu users): `sudo apt install ffmpeg git` (For Arch linux users): `sudo pacman -S ffmpeg git` (For Fedora users): `sudo dnf install ffmpeg git`
(Some distributions already come with Git and FFmpeg preinstalled so this step may be optional.)

> [!IMPORTANT]  
> FFmpeg has to be added to the PATH. (only needed on Windows)

## Getting Started

Clone the repository (git needed) or download the source code of the latest release [here](https://github.com/Eddycrack864/UVR5-UI/releases)

```
git clone https://github.com/Eddycrack864/UVR5-UI.git
```

Then continue with the steps described below

### 1. Installation

Run the installation script based on your operating system:

- **Windows:** Double-click `UVR5-UI-installer.bat` (DONT RUN AS ADMINISTRATOR 🚧).
- **Linux:** Run `UVR5-UI-installer.sh` with `chmod +x UVR5-UI-installer.sh` and `./UVR5-UI-installer.sh`.

### 2. Running UVR5 UI

Start UVR5 UI using:

- **Windows:** Double-click `run-UVR5-UI.bat`.
- **Linux:** Run `run-UVR5-UI.sh` with `chmod +x run-UVR5-UI.sh` and `./run-UVR5-UI.sh`.

### 3. Update UVR5 UI (If you want/need it)

Update UVR5 UI using (git needed):

- **Windows:** Double-click `UVR5-UI-updater.bat`.
- **Linux:** Run `UVR5-UI-updater.sh` with `chmod +x UVR5-UI-updater.sh` and `./UVR5-UI-updater.sh`.

If you find an error when installing or running the program please consult [this troubleshooting file](https://github.com/Eddycrack864/UVR5-UI/blob/main/info/troubleshooting.md) first, if your error is not described there please create an [issue](https://github.com/Eddycrack864/UVR5-UI/issues)

### 4. Debug (If you want/need it)

Check the status of audio-separator core:

- **Windows:** Double-click `status-checker.bat`.
- **Linux:** Run `status-checker.sh` with `chmod +x status-checker.sh` and `./status-checker.sh`.

## Precompiled Version
1. Get the precompiled version (.zip) for your PC:
   - **[Windows](https://huggingface.co/Eddycrack864/UVR5-UI/tree/main/Windows)**
   - **[Linux](https://huggingface.co/Eddycrack864/UVR5-UI/tree/main/Linux)**

2. Extract the .zip file, I recommend using the "extract here" option.
3. You can now use all the features of the normal installation.

> [!NOTE]  
> Still, to update UVR5 UI you need to install Git.

## Docker Instance

A more technical level is required for this type of use. You can use this Jupyter notebook to initialize UVR5 on virtual machines with GPU. This will install the entire UVR5 from the main branch of GitHub.

### Requirements/Recommendations
- Use the docker image `>= ubuntu/ubuntu:20.04`
- At least `20 GB of storage minimum.` (Add more space for your models/training)
- Use Jupyter `>= 7.3.1`
- Configure port forwarding `9999 (UVR5-UI GUI)`
- Install necessary drivers to use the GPU

You can get the notebook here: [Jupyter Notebook](https://github.com/Eddycrack864/UVR5-UI/blob/main/UVR_UI_Jupyter.ipynb) by iroaK


## Contributions
If you want to participate and help me with this project feel free to create an [issue](https://github.com/Eddycrack864/UVR5-UI/issues) if something goes wrong or make a [pull request](https://github.com/Eddycrack864/UVR5-UI/pulls) to improve this project.

Any type of contribution is welcome 💖

If you like this project you can star this repository. I will appreciate a lot 💖💖💖

You can donate to the original UVR5 project here:

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/uvr5)

## TO-DO
* Add more models
* Add more output formats

## Credits
* python-audio-separator by [beveradb](https://github.com/beveradb).
* Special thanks to [Ilaria](https://github.com/TheStingerX) for hosting this space and help 💖
* Thanks to [Mikus](https://github.com/cappuch) for the help with the code.
* Thanks to [Nick088](https://github.com/Nick088Official) for the help to fix roformers.
* Thanks to [yt_dlp](https://github.com/yt-dlp/yt-dlp) devs.
* Separation by link source code and improvements by [NeoDev](https://github.com/TheNeodev).
* Thanks to [ArisDev](https://github.com/aris-py) for porting UVR5 UI to Kaggle and improvements.