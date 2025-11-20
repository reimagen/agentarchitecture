/**
 * Processes a text file and converts it to a single line with numbered sections
 * @param {File} file - The text file to process
 * @returns {Promise<string>} - The processed text as a single line
 */
export const processTextFile = async (file) => {
  const text = await file.text();

  // Split by double newlines or multiple whitespace to identify sections
  const sections = text.split(/\n\s*\n+/);

  // Filter out empty sections and trim whitespace
  const cleanSections = sections
    .map(section => section.trim())
    .filter(section => section.length > 0);

  // Number each section and join into a single line
  const numberedSections = cleanSections.map((section, index) => {
    return `Step ${index + 1}: ${section.replace(/\n/g, ' ')}`;
  });

  return numberedSections.join(' ');
};

/**
 * Processes a file and returns the formatted body for the API request
 * @param {File} file - The text file to process
 * @returns {Promise<Object>} - The JSON body with workflow_text attribute
 */
export const prepareWorkflowBody = async (file) => {
  const workflowText = await processTextFile(file);

  return {
    workflow_text: workflowText
  };
};
