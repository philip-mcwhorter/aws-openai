// see https://github.com/FullStackWithLawrence/aws-openai/blob/main/api/terraform/apigateway_endpoints.tf#L19
import { BACKEND_API_URL, AWS_API_GATEWAY_KEY, OPENAI_EXAMPLES_URL } from "../config";

const SLUG = 'default-interview-questions';

const InterviewQuestions = {
  api_url: BACKEND_API_URL + SLUG,
  api_key: AWS_API_GATEWAY_KEY,
  app_name: "Interview Question Generator",
  assistant_name: "Irene",
  avatar_url: '/applications/InterviewQuestions/Irene.svg',
  background_image_url: '/applications/InterviewQuestions/InterviewQuestions-bg.svg',
  welcome_message: `Hello, I'm Irene, and I can help you create interview questions for your job candidates.`,
  example_prompts: [],
  placeholder_text: `tell Irene about your job posting`,
  info_url: OPENAI_EXAMPLES_URL + SLUG
};

export default InterviewQuestions;
