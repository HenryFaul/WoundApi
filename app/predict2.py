
from keras.models import load_model
from app.models.deeplab import Deeplabv3, relu6, BilinearUpsampling, DepthwiseConv2D
from app.utils.learning.metrics import dice_coef, precision, recall
from app.utils.io.data_custom import save_results_custom, load_test_images, DataGenCustom
from pathlib import Path
from keras.layers import BatchNormalization

# settings
input_dim_x = 224
input_dim_y = 224
color_space = 'rgb'

BASE_DIR = Path(__file__).resolve(strict=True).parent
pred_save_path = f"{BASE_DIR}/static/picture_uploads/generated_predictions/"
file_path_training = f"{BASE_DIR}/training_history/training.hdf5"
#test_path ="{BASE_DIR}/static/picture_uploads/resized_uploads/20240517-064817/"





def make_prediction(current_path, base_url,resized_original):
    

    data_gen = DataGenCustom(current_path+"/", split_ratio=0.0, x=input_dim_x, y=input_dim_y, color_space=color_space)

    x_test, test_label_filenames_list = load_test_images(current_path+"/")

    # ### get mobilenetv2 model

    model = Deeplabv3(input_shape=(input_dim_x, input_dim_y, 3), classes=1)
    
    model = load_model(file_path_training
                       , custom_objects={'recall': recall,
                                         'precision': precision,
                                         'dice_coef': dice_coef,
                                         'relu6': relu6,
                                         'BatchNormalization': BatchNormalization,
                                         'DepthwiseConv2D': DepthwiseConv2D,
                                         'BilinearUpsampling': BilinearUpsampling})

    for image_batch, label_batch in data_gen.generate_data(batch_size=len(x_test), test=True):
        prediction = model.predict(image_batch, verbose=1)
        
        res = save_results_custom(prediction, 'rgb', pred_save_path, test_label_filenames_list, base_url,resized_original)
        return res
