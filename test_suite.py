from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import unittest

class TestFitPeoCalculator(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.fitpeo.com/")
        self.driver.maximize_window()
        calculator_link = self.wait_for_element((By.XPATH, "//div[contains(@class, 'MuiBox-root')]/a/div[text()='Revenue Calculator']"))
        calculator_link.click()


    def tearDown(self):
        self.driver.quit()

    def wait_for_element(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))

    def wait_for_elements(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located(locator))

    def test_navigate_to_calculator(self):
        calculator_link = self.wait_for_element((By.XPATH, "//div[contains(@class, 'MuiBox-root')]/a/div[text()='Revenue Calculator']"))
        
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "MuiInputBase-input")))
        self.assertTrue(calculator_link.is_displayed(), "Failed to navigate to Revenue Calculator")

    def test_adjust_slider(self):
        slider_handle = self.wait_for_element((By.XPATH, "//span[contains(@class, 'MuiSlider-thumb')]//input[@type='range']"))
        actions = ActionChains(self.driver)
        actions.drag_and_drop_by_offset(slider_handle, 93, 0).perform()
        for _ in range(3):
            slider_handle.send_keys(Keys.ARROW_RIGHT)
        
        text_field = self.wait_for_element((By.CLASS_NAME, "MuiInputBase-input"))
        tf_value = text_field.get_attribute("value")
        self.assertEqual(tf_value, "820", f"Text field value is '{tf_value}' it should be '820'")
        
        text_field.click()
        text_field.send_keys(Keys.CONTROL + "a")
        text_field.send_keys(560)
        
        slider_value = slider_handle.get_attribute("value")
        self.assertEqual(slider_value, "560", f"Slider value is '{slider_value}' it should be '560'")

    def _select_cpt_codes(self):
        scroll_script = "window.scrollBy(0, 930)"
        self.driver.execute_script(scroll_script)
        
        cpt_codes = ["CPT-99091", "CPT-99453", "CPT-99454", "CPT-99474"]
        for cpt in cpt_codes:
            try:
                cpt_container = self.wait_for_element((By.XPATH, f"//p[contains(@class, 'MuiTypography-root') and text() = '{cpt}']"))
                parent = cpt_container.find_element(By.XPATH, "./parent::*[contains(@class, 'MuiBox-root')]")
                
                checkbox = parent.find_element(By.CSS_SELECTOR, ".PrivateSwitchBase-input")
                checkbox.click()
                
                self.assertTrue(cpt_container.is_displayed(), f"Failed to select CPT code: {cpt}")
            except Exception as e:
                self.fail(f"Error selecting CPT code {cpt}: {str(e)}")

    def test_validate_total_recurring_reimbursement(self):
        self._select_cpt_codes()
        self.driver.execute_script("window.scrollTo(0, 130)")
        text_field = self.wait_for_element((By.CLASS_NAME, "MuiInputBase-input"))
        text_field.click()
        text_field.send_keys(Keys.CONTROL + "a")
        text_field.send_keys(820)
        
        self.driver.execute_script("window.scrollBy(0, 930)")
        
        reimbursement_parent = self.wait_for_element((By.XPATH, "//p[contains(@class, 'MuiTypography-root') and contains(., 'Total Recurring Reimbursement for all Patients Per Month:')][1]"))
        reimbursement_child = reimbursement_parent.find_element(By.CSS_SELECTOR, "p:nth-of-type(1)")
        reimbursement_value = reimbursement_child.get_attribute("innerText")
        
        self.assertEqual(reimbursement_value, "$110700", f"Reimbursement value is '{reimbursement_value}' it should be '$110700'")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFitPeoCalculator)
    unittest.TextTestRunner().run(suite)
