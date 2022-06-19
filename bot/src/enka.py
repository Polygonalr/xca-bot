from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import base64

# Thanks to https://stackoverflow.com/questions/16462177/selenium-expected-conditions-possible-to-use-or
class AnyEc:
  """ Use with WebDriverWait to combine expected_conditions
      in an OR.
  """
  def __init__(self, *args):
    self.ecs = args
  def __call__(self, driver):
    for fn in self.ecs:
      try:
        res = fn(driver)
        if res:
          return True
          # Or return res if you need the element found
      except:
        pass


# Thanks to https://stackoverflow.com/questions/47424245/how-to-download-an-image-with-python-3-selenium-if-the-url-begins-with-blob
def get_file_content_chrome(driver, uri):
  result = driver.execute_async_script("""
    var uri = arguments[0];
    var callback = arguments[1];
    var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
    var xhr = new XMLHttpRequest();
    xhr.responseType = 'arraybuffer';
    xhr.onload = function(){ callback(toBase64(xhr.response)) };
    xhr.onerror = function(){ callback(xhr.status) };
    xhr.open('GET', uri);
    xhr.send();
    """, uri)
  if type(result) == int :
    raise Exception("Request failed with status %s" % result)
  return base64.b64decode(result)

def extract_enka_image(uid, char):
    # Initialize the browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://enka.shinshin.moe/u/" + str(uid))
    WebDriverWait(driver, 30).until( # Wait for the page to load!
      AnyEc(
        EC.presence_of_element_located((By.CLASS_NAME, "name")),
        EC.presence_of_element_located((By.CLASS_NAME, "Message")),
      )
    )

    if len(driver.find_elements(by=By.CLASS_NAME, value="Message")) != 0:
      driver.quit()
      return "priv"

    # Finding the character
    found = False
    char_list = driver.find_elements(by=By.CLASS_NAME, value="CharacterList")[0].find_elements(by=By.CLASS_NAME, value="avatar")
    for char_icon in char_list:
        char_icon.click()
        char_name = driver.find_elements(by=By.CLASS_NAME, value="name")[0].get_attribute('innerHTML')
        if char.lower() in char_name.lower():
            found = True
            break
    if not found:
        driver.quit()
        return "no"

    driver.find_elements(by=By.CLASS_NAME, value="toolbar")[0].find_elements(by=By.TAG_NAME, value="button")[0].click()
    img_blob = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'UID ')]/img"))
    )
    img_data = get_file_content_chrome(driver, img_blob.get_attribute('src'))
    driver.quit()
    return img_data