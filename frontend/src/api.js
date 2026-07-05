const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";


function formatValidationError(detail) {
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const location = Array.isArray(item.loc)
          ? item.loc
              .filter((part) => part !== "body")
              .join(".")
          : "";

        const message =
          item.msg ||
          "Invalid request value.";

        return location
          ? `${location}: ${message}`
          : message;
      })
      .join("\n");
  }

  if (
    detail &&
    typeof detail === "object"
  ) {
    try {
      return JSON.stringify(
        detail,
        null,
        2,
      );
    } catch {
      return "The server rejected the request.";
    }
  }

  if (typeof detail === "string") {
    return detail;
  }

  return "";
}


async function request(
  endpoint,
  options = {},
) {
  const headers = {
    ...(options.headers || {}),
  };

  if (
    options.body !== undefined &&
    !(options.body instanceof FormData)
  ) {
    headers["Content-Type"] =
      "application/json";
  }

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        ...options,
        headers,
      },
    );
  } catch {
    throw new Error(
      "Could not connect to the VendorGuard backend. Confirm that it is running on http://127.0.0.1:8000.",
    );
  }

  let responseData = null;

  try {
    responseData =
      await response.json();
  } catch {
    responseData = null;
  }

  if (!response.ok) {
    const detailMessage =
      formatValidationError(
        responseData?.detail,
      );

    const message =
      detailMessage ||
      responseData?.message ||
      `Request failed with status ${response.status}.`;

    throw new Error(message);
  }

  return responseData;
}


function normalizeDecision(value) {
  const decisionMap = {
    APPROVE: "APPROVED",
    APPROVED: "APPROVED",

    APPROVE_WITH_CONDITIONS:
      "APPROVED_WITH_CONDITIONS",

    APPROVED_WITH_CONDITIONS:
      "APPROVED_WITH_CONDITIONS",

    REQUEST_MORE_INFORMATION:
      "INFORMATION_REQUESTED",

    INFORMATION_REQUESTED:
      "INFORMATION_REQUESTED",

    REJECT: "REJECTED",
    REJECTED: "REJECTED",
  };

  return decisionMap[value] || value;
}


function normalizeConditions(value) {
  if (Array.isArray(value)) {
    return value
      .map((item) =>
        String(item).trim(),
      )
      .filter(Boolean);
  }

  if (typeof value === "string") {
    return value
      .split(/\r?\n/)
      .map((item) => item.trim())
      .filter(Boolean);
  }

  return [];
}


export async function getVendors() {
  return request("/vendors");
}


export async function startAssessment(
  vendorId,
) {
  if (!vendorId) {
    throw new Error(
      "Vendor ID is required.",
    );
  }

  return request(
    "/assessments",
    {
      method: "POST",
      body: JSON.stringify({
        vendor_id: vendorId,
      }),
    },
  );
}


export async function getAssessments() {
  return request("/assessments");
}


export async function getAssessment(
  assessmentId,
) {
  if (!assessmentId) {
    throw new Error(
      "Assessment ID is required.",
    );
  }

  return request(
    `/assessments/${encodeURIComponent(
      assessmentId,
    )}`,
  );
}


export async function submitReview(
  assessmentId,
  reviewData,
) {
  if (!assessmentId) {
    throw new Error(
      "Assessment ID is required.",
    );
  }

  const reviewerName = String(
    reviewData?.reviewer_name ||
      reviewData?.reviewerName ||
      reviewData?.reviewer_id ||
      "",
  ).trim();

  const reviewerRole = String(
    reviewData?.reviewer_role ||
      reviewData?.reviewerRole ||
      "Security Reviewer",
  ).trim();

  const reason = String(
    reviewData?.reason || "",
  ).trim();

  const decision =
    normalizeDecision(
      reviewData?.decision,
    );

  const conditions =
    normalizeConditions(
      reviewData?.conditions,
    );

  if (!reviewerName) {
    throw new Error(
      "Reviewer name is required.",
    );
  }

  if (!reviewerRole) {
    throw new Error(
      "Reviewer role is required.",
    );
  }

  if (!decision) {
    throw new Error(
      "A human decision is required.",
    );
  }

  if (reason.length < 3) {
    throw new Error(
      "Please enter a review reason of at least 3 characters.",
    );
  }

  if (
    decision ===
      "APPROVED_WITH_CONDITIONS" &&
    conditions.length === 0
  ) {
    throw new Error(
      "Approval with conditions requires at least one condition.",
    );
  }

  return request(
    `/assessments/${encodeURIComponent(
      assessmentId,
    )}/review`,
    {
      method: "POST",
      body: JSON.stringify({
        reviewer_name: reviewerName,
        reviewer_role: reviewerRole,
        decision,
        reason,
        conditions,
      }),
    },
  );
}