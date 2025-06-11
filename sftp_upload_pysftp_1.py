# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 16:15:37 2024

@author: shrihari
"""

import pysftp
import logging


def upload_to_sftp(local_dir,rm_dir,zip_file_name):
    # Logging configuration (change path as needed)
    logging.basicConfig(filename='sftp_upload.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Define your SFTP credentials and server details
    hostname = 'axonpublicstorage.blob.core.windows.net'
    port = 22  # Default SFTP port
    username = 'axonpublicstorage.eox.eox'
    password = '78UfYGZcfYXjQr7QJm5ewbIrCiL6CzG0'
    
    # Define the local and remote paths
    local_file_path = local_dir+'/' + zip_file_name
    remote_directory = '/'+rm_dir
    remote_file_path = f'{remote_directory}/' + zip_file_name

    # Set up the SFTP connection parameters
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None  # Disable host key checking for simplicity

    # Progress callback function
    def print_progress(transferred, total):
        percentage = (transferred / total) * 100
        logging.info(f"Transferred: {transferred} bytes of {total} bytes ({percentage:.2f}%)")
        print(f"Transferred: {transferred} bytes of {total} bytes ({percentage:.2f}%)")
    try:
        # Establish an SFTP connection
        with pysftp.Connection(host=hostname, username=username, password=password, port=port, cnopts=cnopts) as sftp:
            # Upload the file to the specified directory on the SFTP server
            print(f"Uploading {local_file_path} to {remote_file_path}")
            sftp.put(local_file_path, remote_file_path, callback=print_progress)
            print(f"Uploaded {local_file_path} to {remote_file_path}")

    except pysftp.ConnectionException as e:
        print(f"Connection error: {e}")
    except pysftp.CredentialException as e:
        print(f"Credential error: {e}")
    except pysftp.SSHException as e:
        print(f"SSH error: {e}")
    except pysftp.SFTPError as e:
        print(f"SFTP error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# upload_to_sftp('axon_LUST_details_20240807145827.zip')