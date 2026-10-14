import base64
import os
from io import BytesIO

import streamlit as st
from PIL import Image
from openai import OpenAI

st.set_page_config(
    page_title="Sepiddandan AI Studio",
    page_icon="🐾",
    layout="wide",
)

st.markdown("""
<style>
html, body, [class*="css"] { direction: rtl; text-align: right; }
.block-container { padding-top: 1.5rem; max-width: 1200px; }
div[data-testid="stFileUploader"] { direction: rtl; }
</style>
""", unsafe_allow_html=True)

st.title("🐾 استودیو هوش مصنوعی سپیددندان")
st.caption("ساخت و ویرایش عکس‌های تبلیغاتی محصولات پت‌شاپ")

with st.sidebar:
    st.header("تنظیمات")
    api_key = st.text_input(
        "کلید API اوپن‌ای‌آی",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="کلید API را فقط در این برنامه وارد کنید. آن را با کسی به اشتراک نگذارید.",
    )
    model = st.selectbox(
        "مدل تصویر",
        ["gpt-image-2.5-sunburst", "gpt-image-2.5-flare", "gpt-image-1.5"],
        index=0,
        help="در صورت نداشتن دسترسی به مدل انتخابی، مدل دیگری را امتحان کنید.",
    )
    st.info("استفاده از API ممکن است هزینه جداگانه داشته باشد. قبل از تولید، هزینه‌ها و دسترسی حساب خود را بررسی کنید.")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("۱) عکس محصول")
    uploaded = st.file_uploader(
        "عکس اصلی محصول را انتخاب کنید",
        type=["png", "jpg", "jpeg", "webp"],
        help="برای حفظ بهتر جزئیات، عکس واضح و باکیفیت بارگذاری کنید.",
    )
    if uploaded:
        try:
            preview = Image.open(BytesIO(uploaded.getvalue()))
            st.image(preview, caption="عکس اصلی", use_container_width=True)
        except Exception:
            st.error("فایل تصویر قابل خواندن نیست.")

with col_right:
    st.subheader("۲) نوع خروجی")
    mode = st.selectbox(
        "سبک تبلیغ",
        [
            "عکس استودیویی محصول",
            "محصول در کنار سگ یا گربه",
            "بنر تبلیغاتی سایت",
            "پس‌زمینه تمیز و مینیمال",
            "سبک لوکس و پریمیوم",
            "تبلیغ اینستاگرامی",
        ],
    )
    product_name = st.text_input("نام محصول (اختیاری)", placeholder="مثلاً قلاده تنی سگ نژاد کوچک")
    product_category = st.selectbox(
        "دسته‌بندی محصول",
        ["عمومی", "غذای خشک", "تشویقی", "قلاده و هارنس", "اسباب‌بازی", "بهداشتی", "جای خواب و لوازم", "حمل‌ونقل"],
    )
    banner_text = st.text_input("متن روی بنر (اختیاری)", placeholder="مثلاً انتخابی مطمئن برای دوست پشمالوی شما")
    extra = st.text_area(
        "توضیحات اضافه (اختیاری)",
        placeholder="مثلاً پس‌زمینه کرم، نور نرم، محصول در مرکز تصویر...",
        height=100,
    )

st.subheader("۳) حفظ جزئیات محصول")
preserve = st.checkbox(
    "تا حد امکان بسته‌بندی، لوگو، رنگ و شکل محصول اصلی حفظ شود",
    value=True,
)
st.caption("نکته: مدل‌های تصویر ممکن است نوشته‌های ریز یا جزئیات بسته‌بندی را دقیق بازتولید نکنند؛ قبل از انتشار، خروجی را بررسی کنید.")

def build_prompt():
    modes = {
        "عکس استودیویی محصول": (
            "Edit the uploaded image into premium commercial studio product photography. "
            "Use softbox lighting, accurate white balance, realistic contact shadows, crisp details, "
            "a clean neutral background, and balanced e-commerce composition."
        ),
        "محصول در کنار سگ یا گربه": (
            "Create a realistic pet lifestyle advertisement based on the uploaded product. "
            "Show an appropriate dog or cat naturally using or wearing the product. "
            "Keep the product clearly visible, anatomically realistic, and naturally fitted."
        ),
        "بنر تبلیغاتی سایت": (
            "Create a clean professional e-commerce website banner based on the uploaded product. "
            "Use a wide advertising composition with clear negative space for text and a polished commercial look."
        ),
        "پس‌زمینه تمیز و مینیمال": (
            "Improve the uploaded product photo with a clean, minimal, distraction-free background, "
            "soft natural shadows, balanced exposure, and accurate product colors."
        ),
        "سبک لوکس و پریمیوم": (
            "Create premium high-end commercial product photography with controlled studio lighting, "
            "refined composition, realistic texture, elegant restrained background, and natural shadows."
        ),
        "تبلیغ اینستاگرامی": (
            "Create an eye-catching but uncluttered social media advertisement based on the uploaded product. "
            "Use a strong focal point, polished lighting, and a mobile-friendly composition."
        ),
    }
    prompt = modes[mode]
    prompt += (
        "\nBrand context: Sepiddandan Pet, a pet supplies store. "
        "Do not invent product benefits, prices, certifications, or claims."
    )
    if product_name.strip():
        prompt += f"\nProduct name supplied by user: {product_name.strip()}."
    prompt += f"\nProduct category: {product_category}."
    if banner_text.strip():
        prompt += f"\nRequested visible banner text: {banner_text.strip()}. Render text only if it can be written accurately; otherwise leave clean space for adding text later."
    if preserve:
        prompt += (
            "\nPRODUCT PRESERVATION IS IMPORTANT: keep the original product identity, silhouette, "
            "proportions, colors, logo, packaging, labels, straps, buckles, stitching, and visible details as close as possible. "
            "Do not redesign the product or add features that are not present in the source image."
        )
    if extra.strip():
        prompt += f"\nAdditional user instructions: {extra.strip()}."
    prompt += (
        "\nOutput should look like realistic professional commercial photography, not an illustration. "
        "Avoid clutter, unnecessary props, fake labels, distorted packaging, and exaggerated effects."
    )
    return prompt

if st.button("✨ ساخت عکس تبلیغاتی", type="primary", use_container_width=True):
    if not api_key:
        st.error("ابتدا کلید API را در نوار کناری وارد کنید.")
    elif not uploaded:
        st.error("ابتدا عکس محصول را بارگذاری کنید.")
    else:
        try:
            with st.spinner("در حال ساخت تصویر تبلیغاتی؛ ممکن است کمی زمان ببرد..."):
                client = OpenAI(api_key=api_key)
                file_tuple = (uploaded.name, uploaded.getvalue(), uploaded.type or "image/png")
                response = client.images.edit(
                    model=model,
                    image=file_tuple,
                    prompt=build_prompt(),
                    input_fidelity="high" if model == "gpt-image-1.5" else None,
                )
                image_data = response.data[0].b64_json
                result_bytes = base64.b64decode(image_data)
                st.session_state["result_image"] = result_bytes
                st.session_state["result_name"] = "sepiddandan_ad.png"
                st.session_state["result_prompt"] = build_prompt()
        except Exception as e:
            st.error("ساخت تصویر انجام نشد. متن خطا:")
            st.code(str(e))
            st.caption("کلید API، اعتبار حساب، دسترسی به مدل و فرمت/حجم عکس را بررسی کنید.")

if st.session_state.get("result_image"):
    st.divider()
    st.subheader("۴) خروجی آماده بررسی")
    st.image(st.session_state["result_image"], caption="تصویر تولیدشده", use_container_width=True)
    st.download_button(
        "⬇️ دانلود تصویر PNG",
        data=st.session_state["result_image"],
        file_name=st.session_state.get("result_name", "sepiddandan_ad.png"),
        mime="image/png",
        use_container_width=True,
    )
    with st.expander("نمایش دستور استفاده‌شده"):
        st.text(st.session_state.get("result_prompt", ""))

st.divider()
st.caption("Sepiddandan AI Studio — نسخه اولیه محلی. این برنامه مستقیماً به سایت فروشگاه وصل نیست و تصاویر را خودکار منتشر نمی‌کند.")
