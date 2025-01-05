<template>
  <div>
    <h2>Image Resizer</h2>

    <!-- File input to select image -->
    <input id="uploader" type="file" @change="imageUploadHandler">

    <!-- Button to trigger image upload -->
    <button :disabled="!fileSelected" @click="imageUploader">Upload Image</button>

    <!-- Display selected file name -->
    <p v-if="fileSelected">Image selected: {{ imageFileName }}</p>
    <br>
    <p v-if="uploadSuccess">Image {{imageFileName}} uploaded successfully!!</p>

    <p v-if="processingMessage" v-html="processingMessage"></p>

    <a v-if="downloadUrl" :href="downloadUrl" :download="downloadName">Click here to download the resized {{ this.imageFileName }}</a>

<!--    <button @click="resetPage">Reset</button>-->
  </div>
</template>

<script>
import { BlobServiceClient } from "@azure/storage-blob";

export default {
  data() {
    return {
      fileSelected: false,
      imageFileName: "",
      imageFile: null,
      uploadSuccess: false,
      downloadUrl: null,
      downloadName: "",
      processingMessage: "",
      sasToken: process.env.VUE_APP_SAS_TOKEN,
    };
  },

  methods: {
    //Page Resetter
    resetPage() {
    // Reset file input
    this.imageFile = null;

    // Reset image name and success message
    this.imageFileName = '';
    this.uploadSuccess = false;
    this.processingMessage = "";

    // Clear download URL
    this.downloadUrl = null;
  },


    // Handler for file selection
    imageUploadHandler(event) {
      this.resetPage();
      this.imageFile = event.target.files[0];  // Get the first file selected by the user
      this.imageFileName = this.imageFile.name; // Store the file name
      console.log("File selected:", this.imageFileName);  // Log selected file
      this.fileSelected = true;  // Mark file as selected
    },

    // Image Downloader function works as well although redundant as the containers are set for public access.

    async imageDownloader(retries=5) {

      for (let attempt=1; attempt<=retries; attempt++) {
        try {
          this.processingMessage += "Processing......<br>";



          const storageAcc = new BlobServiceClient(
              `https://21f3001584foundation.blob.core.windows.net?${this.sasToken}`
          );

          console.log("Waiting for 5 seconds to allow processing...");
          await new Promise(resolve => setTimeout(resolve, 5000));

          const processedImagesContainer = storageAcc.getContainerClient("processed-images");
          console.log("Download Container Client Created Successfully")

          const processedImagesBBC = processedImagesContainer.getBlockBlobClient(`PROCESSED-images/${this.imageFileName}`);
          console.log("Download BBC Created Successfully")


          // Download the blob's content
          const downloadResponse = await processedImagesBBC.download(0);
          console.log("Download Response Created Successfully")


          // Read the downloaded data as a blob
          const blob = await downloadResponse.blobBody;
          console.log("Download Response Blob Created Successfully")

          // Create a temporary URL to download the blob
          this.downloadUrl = URL.createObjectURL(blob);
          console.log("Download URL Created Successfully")

          this.downloadName = `Resized_${this.imageFileName}`

          return  // exit out of the loop
        } catch (error) {
          console.error("Error downloading image:", error.message);
          console.log(error.stack);
        }
    }


  },


    // Upload image to Azure Blob Storage
    async imageUploader() {
      try {

        console.log("Starting image upload...");

        // Securely fetch the Azure connection string from an environment variable

        //
        // console.log("Connection string set");
        //
        // // Instantiate the BlobServiceClient using the connection string
        // const storageAcc = BlobServiceClient.fromConnectionString(connectionString);

         // Replace with your SAS token as using Azure connection String was leading to a "Buffer not defined error" on the browser's side
        // const sasToken = "sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2025-01-05T15:42:08Z&st=2025-01-05T07:42:08Z&spr=https,http&sig=aKI92R04r9VHoh7jeXwr2bziHBoMQs%2FIv%2BqOxhobs9s%3D";
        const storageAcc = new BlobServiceClient(
          `https://21f3001584foundation.blob.core.windows.net?${this.sasToken}`
        );

        console.log("BlobServiceClient created");

        // Get the container client (replace "images" with your container name)
        const imagesContainer = storageAcc.getContainerClient("images");

        console.log("Container client created for 'images' container");

        // Create a BlockBlobClient for the selected file
        const imagesBBC = imagesContainer.getBlockBlobClient(this.imageFileName);

        console.log("BlockBlobClient created for file:", this.imageFileName);

        // Directly upload the file object (no need to convert it to a buffer)
        const uploadResponse = await imagesBBC.uploadData(this.imageFile);

        console.log("Image uploaded successfully:", uploadResponse);

        this.uploadSuccess = true;

        // this.downloadUrl = `https://21f3001584foundation.blob.core.windows.net/processed-images/PROCESSED-images/${this.imageFileName}`

        await this.imageDownloader()
      } catch (error) {
        console.error("Error uploading image:", error.message);
        console.log(error.stack)
      }
    },
  },




};
</script>

<style scoped>
</style>
