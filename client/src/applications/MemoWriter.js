// see https://github.com/FullStackWithLawrence/aws-openai/blob/main/api/terraform/apigateway_endpoints.tf#L19
import { BACKEND_API_URL, AWS_API_GATEWAY_KEY, OPENAI_EXAMPLES_URL } from "../config";

const SLUG = 'default-memo-writer';

const MemoWriter = {
  api_url: BACKEND_API_URL + SLUG,
  api_key: AWS_API_GATEWAY_KEY,
  app_name: "Memo Writer",
  assistant_name: "Guillermo",
  avatar_url: '/applications/MemoWriter/Guillermo.svg',
  background_image_url: '/applications/MemoWriter/MemoWriter-bg.jpg',
  welcome_message: `Hello, I'm Guillermo, an executive assistant who can help you write a memo.`,
  example_prompts: [],
  placeholder_text: `tell Guillermo what this memo is about`,
  info_url: OPENAI_EXAMPLES_URL + SLUG
};

export default MemoWriter;
