# Property Rental Interest Prediction Web App
A software to predict how popular an apartment retal listing based onthe listing content like text description, photos, number of bedrooms, price,.... The data is provided from renthop.com, an apartment listing site with the apartments are located in New York City. Specifically, for a listing_id, we want to know whether the customer has a `low`, `medium`, or `high` interest.

Research Questions:
- 2. Model 1: Based on the tabular input of the user (without extracted features from image), can we predict the interest level. 
  - Customer: Agent
  - Classical ML.
- 3. Model 2: Based on the tabular input of the user and the image, can we predict the interest level.
  - Customer: Agent
  - Yolo
  - Classical ML
  - Dataset with images only
- 4. Model 3: Based on the input data, can we generate the image of the room?
  - Fine-tune Deep Learning
  - Customer: Agent
- 5. Model 4: Usage of ChatGPT 
  - Customer: Renter
  - Customer service bot to answer the FAQs about the NYC rental market using the dataset as knowledge base and analysis.
  - Hard: from the chat, provide the listing of the relevant property to select?
    - https://www.youtube.com/watch?v=EE1Y2enHrcU
    - https://www.youtube.com/watch?v=4qNwoAAfnk4&t=17s

## About
### Dataset
The datasets can be found [here]((https://www.kaggle.com/competitions/two-sigma-connect-rental-listing-inquiries/data?select=train.json.zip)).
- `train.json`: the training set.
- `images_sample.zip`: listing images organized by listing_id (a sample of 100 listings)
- `Kaggle-renthop.7z`: listing images organized by listing_id. Total size: 78.5 GB compressed.

**Note**: for this project, we will consider the training dataset as a full-dataset, as our goal is not to beat the competition, but to build a tool for data analysis and usages.

## Development Phases

### Phase 1. EDA [ANALYSIS] - DONE
- Explore the dataset, reveal underlying information by plotting static plots for the following feature type, and preprocess the dataset.


### Phase 2. Data Processing [ANALYSIS] - DONE
- Data preprocessing with Pretrained model
  - Sentimental Extraction.
  - Feature Extraction
  - Image Feature Extraction

### Phase 3. ML Modeling [ANALYSIS] - DONE
- **Model 1**: Based on the tabular input of the user (without extracted features from image), can we predict the interest level. 
  - Customer: Agent
  - Classical ML.
- **Model 2**: Based on the tabular input of the user and the image, can we predict the interest level.
  - Customer: Agent
  - Yolo
  - Classical ML
  - Dataset with images only
- **Model 3**: Based on the tabular input of the user (without extracted features from image), can we predict the price. 
  - Customer: Agent + Renter
  - Classical ML.
- **Model 4**: Based on the tabular input of the user and the image, can we predict the price.
  - Customer: Agent
  - Yolo
  - Classical ML
  - Dataset with images only

### Phase 4. Dash Visualization Development [UI + ANALYSIS]
- Dataset analysis, convert all to plotly.
- Map Visualization: Use dash-leaflet or plotly.express to plot rental listings on a map. Users could filter by price range, number of bedrooms/bathrooms, or interest level.
- Price Distribution: Interactive histograms or KDE plots for price where users can filter based on number of bedrooms, bathrooms, or location.
- Feature Correlation: Heatmaps that update based on selected features to show correlations dynamically.
- Interactive Table: Display a searchable and filterable table of listings where users can sort by different features like price, number of bedrooms, or interest level.

### Phase 5. Real-time Prediction (data, image) with Flask [UI]
- **Model 1**: Based on the tabular input of the user (without extracted features from image), can we predict the interest level. 
  - Customer: Agent
  - Classical ML.
- **Model 2**: Based on the tabular input of the user and the image, can we predict the interest level.
  - Customer: Agent
  - Yolo
  - Classical ML
  - Dataset with images only
- **Model 3**: Based on the tabular input of the user (without extracted features from image), can we predict the price. 
  - Customer: Agent + Renter
  - Classical ML.
- **Model 4**: Based on the tabular input of the user and the image, can we predict the price.
  - Customer: Agent
  - Yolo
  - Classical ML
  - Dataset with images only

### Phase 6. Image Generation [UI + UX]
- If have time, may be develop from scratch - diffusion model.
- Initially: has a Q/A > generate images (based on the info we learn) - Model 2
- ChatBox functionality (model)
- **Model 5**: Based on the input data, can we generate the image of the room?
  - Fine-tune Deep Learning
  - Customer: Agent

### Phase 7. Chatbot Development
- **Model 6**: Usage of ChatGPT 
  - Customer: Renter
  - Customer service bot to answer the FAQs about the NYC rental market using the dataset as knowledge base and analysis.
  - Hard: from the chat, provide the listing of the relevant property to select?
    - https://www.youtube.com/watch?v=EE1Y2enHrcU
    - https://www.youtube.com/watch?v=4qNwoAAfnk4&t=17s

### Phase 8. Mobile Development [UI + UX]
- Task 1: Upload images and make prediction (help buyer evaluate the house).
- Task 2: Image generation based on input (help client the house)

### Phase 9. PyTest

### Phase 10. Report & Presentation

## Architecture

## Reproduction

## Demo

## Presentation & Report

## References
[1] “Two Sigma Connect: Rental Listing Inquiries | Kaggle,” Kaggle.com, 2023. https://www.kaggle.com/competitions/two-sigma-connect-rental-listing-inquiries/data?select=train.json.zip (accessed Nov. 23, 2023).
‌