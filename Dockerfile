FROM ubuntu:18.04

WORKDIR /opt
COPY . /opt

USER root

RUN apt-get update
RUN apt-get install -y python3.6-dev \
                       python3-pip \
                       wget \
                       gdal-bin \
                       libgdal-dev \
                       libspatialindex-dev \
                       build-essential \
                       software-properties-common \
                       apt-utils
RUN add-apt-repository ppa:ubuntugis/ubuntugis-unstable
RUN apt-get update
RUN apt-get install -y libgdal-dev
RUN pip3 install -r requirements.txt
RUN wget http://download.osgeo.org/libspatialindex/spatialindex-src-1.7.1.tar.gz
RUN tar -xvf spatialindex-src-1.7.1.tar.gz
RUN cd spatialindex-src-1.7.1/ && ./configure && make && make install
RUN ldconfig
RUN add-apt-repository ppa:ubuntugis/ppa
RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal

#Previous, deprecated EXIF tool version
#RUN wget https://exiftool.org/Image-ExifTool-12.05.tar.gz
#RUN tar -xvf Image-ExifTool-12.05.tar.gz
#RUN cd Image-ExifTool-12.05 && perl Makefile.PL && make test && make install

# New EXIF tool version
RUN wget https://exiftool.org/Image-ExifTool-12.29.tar.gz
RUN tar -xvf Image-ExifTool-12.29.tar.gz
RUN cd Image-ExifTool-12.29 && perl Makefile.PL && make test && make install
RUN echo "export LANGUAGE=en_US.UTF-8">>~/.bash_profile

ENTRYPOINT [ "/usr/bin/python3", "/opt/uav_thermal_calibration.py" ]
