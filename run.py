from SourceStream import SourceStream

from SourceStream.vendor.SplashPyUtils import logger

if __name__=="__main__":
    try:
        SourceStream.main()
    except KeyboardInterrupt:
        logger.log.info("Interrupt signal received.")
