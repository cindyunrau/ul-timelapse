# Ultimaker Timelapse
Timelapse generation for the Ultimaker 3D Printer onboard camera. The system supports multiple printers, manages print jobs, captures live feed images, and compiles captured images into a timelapse video.

Start the program on the same network as the printers and it will automatically connect to ultimakers api and start tracking the statuses of the printers and the print jobs. The resulting .mp4 file will have the same name as the print job itself. 
    
## Installation
1. Clone the repository
```
git clone https://github.com/cindyunrau/ul-timelapse.git
```
2. Install the required dependencies
```
pip install -r requirements.txt
```
## Usage  
    python timelapse.py -ip {IP Addresses} --out_dir {Path to where the timelapse videos should be stored}

## Dependencies

- ffmpeg
- shuttil
- requests==2.32.3
- urllib3==1.26.15
- logging
- argparse
- subprocess

## Contributing
Contributions are welcome! Please feel free to submit a pull request or report an issue.