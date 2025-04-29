<script setup>
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";

// State management
const pdfFile = ref(null);
const pptFile = ref(null);
const paperSummary = ref(null);
const pptData = reactive({
  title: "",
  themes: {},
});
const selectedTheme = ref("");
const newThemeName = ref("");
const paperName = ref("");
const existingPptData = reactive({
  title: "",
  themes: {},
});
const selectedExistingTheme = ref("");
const newExistingThemeName = ref("");
const showNewThemeForm = ref(false);

// PDF file handling
const handlePdfChange = (file) => {
  if (file && file.raw.type === "application/pdf") {
    pdfFile.value = file;
    ElMessage.success("PDF file selected");
  } else {
    ElMessage.error("Please select a PDF file");
  }
  return false; // Prevent automatic upload
};

const handlePdfRemove = (file) => {
  pdfFile.value = "";
};

// PPT file handling
const handlePptChange = (file) => {
  console.log(file);
  if (
    file &&
    file.raw.type ===
      "application/vnd.openxmlformats-officedocument.presentationml.presentation"
  ) {
    pptFile.value = file;
    ElMessage.success("PPT file selected");
  } else {
    ElMessage.error("Please select a PPTX file");
  }
  return false; // Prevent automatic upload
};

// Process PDF:2. submit the pdf file to the backend
const processPdf = async () => {
  if (!pdfFile.value) {
    ElMessage.warning("Please select a PDF file first");
    return;
  }

  const formData = new FormData();
  formData.append("pdf", pdfFile.value.raw);

  try {
    const response = await fetch("http://localhost:8000/pdf/summarize", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to process PDF");
    }

    const result = await response.json();
    ElMessage.success(result.message);
    paperSummary.value = result; // Save the entire result object
    paperName.value = result.paper_name; // Set the paper name from response
  } catch (error) {
    console.error("Error processing PDF:", error);
    ElMessage.error(error.message || "Failed to process PDF");
  }
};

// Process PPT
const processPpt = async () => {
  if (!pptFile.value) {
    ElMessage.warning("Please select a PPT file first");
    return;
  }

  const formData = new FormData();
  formData.append("ppt", pptFile.value.raw);

  try {
    const response = await fetch("http://localhost:8000/ppt/process", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to process PPT");
    }

    const result = await response.json();
    ElMessage.success(result.message);
    existingPptData.title = result.title;
    existingPptData.themes = result.themes;
  } catch (error) {
    console.error("Error processing PPT:", error);
    ElMessage.error(error.message || "Failed to process PPT");
  }
};

// Create new theme
const createNewTheme = () => {
  if (newThemeName.value && paperSummary.value) {
    if (!pptData.themes[newThemeName.value]) {
      pptData.themes[newThemeName.value] = [];
    }

    // Push the entire paper summary object to the theme
    pptData.themes[newThemeName.value].push(paperSummary.value);
    newThemeName.value = "";
    ElMessage.success("New theme created successfully");
    console.log(pptData);
  } else {
    ElMessage.warning("Please enter a theme name and process a PDF first");
  }
};

// Add to existing theme
const addToExistingTheme = () => {
  if (selectedExistingTheme.value && paperSummary.value) {
    if (!existingPptData.themes[selectedExistingTheme.value]) {
      existingPptData.themes[selectedExistingTheme.value] = [];
    }
    existingPptData.themes[selectedExistingTheme.value].push(
      paperSummary.value
    );

    ElMessage.success("Paper added to theme successfully");
  } else {
    ElMessage.warning("Please select a theme and process a PDF first");
  }
};

// Add new theme to existing PPT
const addNewThemeToExistingPpt = () => {
  if (
    newExistingThemeName.value &&
    !existingPptData.themes[newExistingThemeName.value]
  ) {
    existingPptData.themes[newExistingThemeName.value] = [];
    newExistingThemeName.value = "";
    ElMessage.success("New theme added successfully");
  } else if (existingPptData.themes[newExistingThemeName.value]) {
    ElMessage.warning("Theme already exists");
  } else {
    ElMessage.warning("Please enter a theme name");
  }
};

// Generate updated PPT
const generateUpdatedPpt = async () => {
  try {
    console.log(existingPptData);
    const response = await fetch("http://localhost:8000/generate-ppt", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(existingPptData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to generate PPT");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${existingPptData.title || "presentation"}.pptx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    ElMessage.success("PPT generated successfully");
  } catch (error) {
    console.error("Error generating PPT:", error);
    ElMessage.error(error.message || "Failed to generate PPT");
  }
};

// Generate PPT
const generatePpt = async () => {
  try {
    const response = await fetch("http://localhost:8000/generate-ppt", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(pptData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to generate PPT");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${pptData.title || "presentation"}.pptx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    ElMessage.success("PPT generated successfully");
  } catch (error) {
    console.error("Error generating PPT:", error);
    ElMessage.error(error.message || "Failed to generate PPT");
  }
};
</script>

<template>
  <div class="paper-manager">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>Paper Management System</h2>
        </div>
      </template>

      <!-- Main Sections Row -->
      <el-row :gutter="20">
        <!-- PDF Upload Section -->
        <el-col :span="8">
          <el-card class="section">
            <template #header>
              <h3>Upload PDF</h3>
            </template>
            <el-upload
              class="upload-demo"
              drag
              :auto-upload="false"
              :on-change="handlePdfChange"
              :on-remove="handlePdfRemove"
              accept=".pdf"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                Drop PDF file here or <em>click to upload</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">Only PDF files are accepted</div>
              </template>
            </el-upload>
            <div class="button-container">
              <el-button
                type="primary"
                @click="processPdf"
                :disabled="!pdfFile"
              >
                Process PDF
              </el-button>
            </div>
          </el-card>
        </el-col>

        <!-- PPT Management Section -->
        <el-col :span="8">
          <el-card class="section">
            <template #header>
              <h3>PPT Management</h3>
            </template>

            <!-- Upload Existing PPT -->
            <el-upload
              class="upload-demo"
              drag
              :auto-upload="false"
              :on-change="handlePptChange"
              accept=".pptx"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                Drop PPT file here or <em>click to upload</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">Only PPTX files are accepted</div>
              </template>
            </el-upload>
            <div class="button-container">
              <el-button
                type="primary"
                @click="processPpt"
                :disabled="!pptFile"
              >
                Process PPT
              </el-button>
            </div>

             <!-- Add New Theme Option -->
            <el-form
              v-if="Object.keys(existingPptData.themes).length"
              class="theme-form"
            >
              <el-form-item label="Add New Theme">
                <el-switch
                  v-model="showNewThemeForm"
                  active-text="Yes"
                  inactive-text="No"
                />
              </el-form-item>
            </el-form>

            <!-- Add New Theme Form -->
            <el-form
              v-if="
                Object.keys(existingPptData.themes).length && showNewThemeForm
              "
              class="theme-form"
            >
              <el-form-item label="New Theme Name">
                <el-input
                  v-model="newExistingThemeName"
                  placeholder="Enter new theme name"
                />
              </el-form-item>
              <el-form-item>
                <el-button
                  type="success"
                  @click="addNewThemeToExistingPpt"
                  class="theme-button"
                >
                  Add New Theme
                </el-button>
              </el-form-item>
            </el-form>

            <!-- Theme Selection for Existing PPT -->
            <el-form
              v-if="Object.keys(existingPptData.themes).length"
              class="theme-form"
            >
              <el-form-item label="Select Theme">
                <el-select
                  v-model="selectedExistingTheme"
                  placeholder="Select theme"
                  class="theme-select"
                >
                  <el-option
                    v-for="(theme, name) in existingPptData.themes"
                    :key="name"
                    :label="name"
                    :value="name"
                  />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="addToExistingTheme"
                  :disabled="
                    !selectedExistingTheme || !paperSummary || !pdfFile
                  "
                  class="theme-button"
                >
                  Add to Selected Theme
                </el-button>
              </el-form-item>
            </el-form>

            <!-- Current PPT Structure Preview -->
            <div
              v-if="Object.keys(existingPptData.themes).length"
              class="preview-section"
            >
              <el-card class="preview-card">
                <template #header>
                  <div class="preview-header">
                    <h4>
                      Current PPT: {{ existingPptData.title || "Untitled" }}
                    </h4>
                  </div>
                </template>
                <div class="theme-list">
                  <div
                    v-for="(papers, themeName) in existingPptData.themes"
                    :key="themeName"
                    class="theme-item"
                  >
                    <el-tag
                      :type="
                        themeName === selectedExistingTheme ? 'success' : 'info'
                      "
                      effect="plain"
                    >
                      {{ themeName }}
                    </el-tag>
                    <span class="paper-count"
                      >({{ papers.length }} papers)</span
                    >
                  </div>
                </div>
              </el-card>
            </div>

            <!-- Generate Updated PPT Button -->
            <div
              class="generate-section"
              v-if="Object.keys(existingPptData.themes).length"
            >
              <el-button
                type="success"
                @click="generateUpdatedPpt"
                class="generate-button"
                :disabled="!pdfFile"
              >
                Generate Updated PPT
              </el-button>
            </div>
          </el-card>
        </el-col>

        <!-- Create New PPT Section -->
        <el-col :span="8">
          <el-card class="section">
            <template #header>
              <h3>Create New PPT</h3>
            </template>
            <el-form class="create-form">
              <el-form-item label="PPT Title">
                <el-input
                  v-model="pptData.title"
                  placeholder="Enter PPT title"
                />
              </el-form-item>
              <el-form-item label="Paper Name" v-if="paperName">
                <el-input v-model="paperName" disabled />
              </el-form-item>
              <el-form-item label="New Theme">
                <el-input
                  v-model="newThemeName"
                  placeholder="Enter new theme name"
                />
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="createNewTheme"
                  :disabled="!paperSummary || !newThemeName"
                  class="create-button"
                >
                  Create New Theme
                </el-button>
              </el-form-item>
            </el-form>

            <!-- Current PPT Structure Preview -->
            <div
              v-if="Object.keys(pptData.themes).length"
              class="preview-section"
            >
              <el-card class="preview-card">
                <template #header>
                  <div class="preview-header">
                    <h4>Current PPT: {{ pptData.title || "Untitled" }}</h4>
                  </div>
                </template>
                <div class="theme-list">
                  <div
                    v-for="(papers, themeName) in pptData.themes"
                    :key="themeName"
                    class="theme-item"
                  >
                    <el-tag type="success" effect="plain">{{
                      themeName
                    }}</el-tag>
                    <span class="paper-count"
                      >({{ papers.length }} papers)</span
                    >
                  </div>
                </div>
              </el-card>
            </div>

            <!-- Generate New PPT Button -->
            <div class="generate-section">
              <el-button
                type="success"
                @click="generatePpt"
                :disabled="!Object.keys(pptData.themes).length || !pdfFile"
                class="generate-button"
              >
                Generate New PPT
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Summary Section Row -->
      <el-row v-if="paperSummary" class="summary-row">
        <el-col :span="24">
          <el-card class="summary-card">
            <template #header>
              <div class="summary-header">
                <h3>Paper Summary</h3>
                <el-tag type="success" effect="dark">Processed</el-tag>
              </div>
            </template>

            <el-descriptions :column="1" border>
              <el-descriptions-item label="Paper Name">
                <div class="summary-content">
                  {{ paperSummary.paper_name }}
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="Content Summary">
                <div class="summary-content">
                  {{ paperSummary.summary.content_summary }}
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="Contributions">
                <div class="summary-content">
                  {{ paperSummary.summary.contribution }}
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="Methodology">
                <div class="summary-content">
                  {{ paperSummary.summary.method }}
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="Comparison">
                <div class="summary-content">
                  {{ paperSummary.summary.comparison }}
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="Limitations & Future Work">
                <div class="summary-content">
                  {{ paperSummary.summary.limitations_and_future_work }}
                </div>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<style scoped>
.paper-manager {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.section {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-upload {
  width: 100%;
}

.el-upload-dragger {
  width: 100%;
}

.button-container {
  margin-top: 1rem;
  text-align: center;
}

.summary-row {
  margin-top: 2rem;
}

.summary-card {
  width: 100%;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-content {
  white-space: pre-wrap;
  line-height: 1.6;
  padding: 0.5rem 0;
}

.theme-form {
  margin-top: 1rem;
}

.theme-select {
  width: 100%;
}

.create-form {
  margin-top: 1rem;
}

.generate-section {
  margin-top: auto;
  padding-top: 1rem;
  text-align: center;
}

:deep(.el-card__header) {
  padding: 10px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-button) {
  width: 100%;
}

:deep(.el-descriptions__label) {
  width: 150px;
  font-weight: bold;
  background-color: #f5f7fa;
}

:deep(.el-descriptions__content) {
  padding: 12px;
}

.preview-section {
  margin-top: 1rem;
}

.preview-card {
  margin-bottom: 1rem;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-header h4 {
  margin: 0;
  font-size: 1rem;
}

.theme-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.theme-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.paper-count {
  font-size: 0.8rem;
  color: #909399;
}
</style>
