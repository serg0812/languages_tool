import replicate
import requests
from openai import OpenAI

def generate_image(text):
    input = {
        "prompt": f"{text}",
        "aspect_ratio":"1:1",
        "steps":25,
        "guidance":3,
        "interval":2,
        "safety_tolerance":5,
        #"seed":3,
        "output_format":"png",
        "output_quality":80
    }

    output = replicate.run(
        "black-forest-labs/flux-pro",
        input=input,
    )
    print(output)
    photo_url=output

    # Downloading the image
    photo_response = requests.get(photo_url)
    if photo_response.status_code == 200:
        # Saving the image as a PNG file
        with open('./photos/output_sentence.png', 'wb') as image_file:
            image_file.write(photo_response.content)
        print("Image successfully downloaded")
    else:
        print(f"Failed to download image. HTTP Status Code: {photo_response.status_code}")

