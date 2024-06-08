# streamlit run "C:/Users/ssb70/OneDrive/바탕 화면/code8/code8/실습 코드/P08_CH02_profile_generation/P08_CH02_02_streamlit_enhancing_profile_using_prompt_engineering.py"
import streamlit as st
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field


class InstroList(BaseModel):
    intro_list: List[str] = Field(description="소개팅 인사말 후보 리스트")

def generate_intro(api_key, name, age, gender, major, location, bio):
    st.write(f"API Key: {api_key}")  # 디버깅을 위해 API 키 출력 (생산 환경에서는 제거)
    model = ChatOpenAI(model="gpt-4-turbo-preview", temperature=1.0, openai_api_key=api_key)
    parser = JsonOutputParser(pydantic_object=InstroList)
    format_instructions = parser.get_format_instructions()

    human_prompt_template = HumanMessagePromptTemplate.from_template(
                                "이름: {name}, 나이: {age}, 성별: {gender}, 전공: {major}, 지역: {location}, 자기소개: {bio}\n"
                                "위 프로필을 참고해서 소개팅 앱에서 사용 할 것 같은 소개팅에 어울리는 멋진 인삿말 후보 3개 만들어줘, 짧고 간결하게\n{format_instructions}")

    prompt_template = ChatPromptTemplate.from_messages(
        [
            human_prompt_template,
        ])
    prompt_template = prompt_template.partial(format_instructions=format_instructions)
    intro_gen_chain = prompt_template | model | parser
    profile = {"name": name,
               "age": age,
               "gender": gender,
               "major": major,
               "location": location,
               "bio": bio}

    out = intro_gen_chain.invoke(profile)
    return out['intro_list']

# 앱 제목 설정
st.title('🖋️ 멋진 인사말 생성기')

# OpenAI API 키 입력
api_key = st.text_input("OpenAI API Key", type="password")

if api_key:
    # 사용자 입력 양식
    with st.form("profile_form"):
        st.subheader("당신의 프로필 입력해주세요!")

        # 사용자 기본 정보 입력
        name = st.text_input("이름")
        age = st.number_input("나이", min_value=20, max_value=29, step=1)
        location = st.text_input("지역")
        gender = st.selectbox("성별", ["남성", "여성"])
        major = st.text_input("전공")
        bio = st.text_area("소개", placeholder="자신에 대해 알려주세요. 취미, 관심사 등을 포함할 수 있습니다.")

        # 폼 제출 버튼
        submitted = st.form_submit_button("인사말 생성하기")

        if submitted:
            with st.spinner("인사말 생성중..."):
                try:
                    intro_candidate_list = generate_intro(api_key, name=name, age=age, gender=gender, major=major, location=location, bio=bio)
                    st.success("프로필이 생성되었습니다!")

                    # 사용자 프로필 표시
                    with st.container():
                        st.subheader(f"{name}의 프로필")
                        st.text(f"이름: {name}")
                        st.text(f"나이: {age}")
                        st.text(f"성별: {gender}")
                        st.text(f"전공: {major}")
                        st.text(f"위치: {location}")
                        st.text(bio)

                    with st.container():
                        st.subheader("생성된 인사말")
                        st.markdown("\n".join([f"- {candi}" for candi in intro_candidate_list]))

                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")
else:
    st.warning("OpenAI API Key를 입력해주세요.")

