document.getElementById('start-button').addEventListener('click', async () => {
  const name = document.getElementById('name').value;
  const comment = document.getElementById('comment').value;
  const attendanceStr = document.getElementById('attendances').value;

  const attendances = {};
  for (let i = 0; i < attendanceStr.length; i++) {
    if (['○', '△', '×'].includes(attendanceStr[i])) {
        attendances[i + 1] = attendanceStr[i];
    }
  }

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: fillTheForm,
    args: [name, comment, attendances],
  });
});

async function fillTheForm(name, comment, attendances) {
  // This function runs in the context of the web page

  function waitForElement(selector, timeout = 5000) {
    return new Promise((resolve, reject) => {
      const interval = 100;
      const endTime = Date.now() + timeout;

      const check = () => {
        const el = document.querySelector(selector);
        if (el && el.offsetParent !== null) {
          resolve(el);
        } else if (Date.now() > endTime) {
          reject(new Error(`Element not found or not visible: ${selector}`));
        } else {
          setTimeout(check, interval);
        }
      };
      check();
    });
  }

  try {
    let nameInput = document.querySelector('input[name="name"]');

    if (!nameInput || nameInput.offsetParent === null) {
      const addButton = await waitForElement('#add_btn');
      addButton.click();
    }

    nameInput = await waitForElement('input[name="name"]');
    nameInput.value = name;
    nameInput.dispatchEvent(new Event('input', { bubbles: true }));

    const commentInput = await waitForElement('input[name="hitokoto"]');
    commentInput.value = comment;
    commentInput.dispatchEvent(new Event('input', { bubbles: true }));

    // --- FINAL REVISED LOGIC FOR ATTENDANCE ---
    const attendanceRows = document.querySelectorAll('.choice-table tbody tr');
    if (attendanceRows.length === 0) {
        throw new Error("Attendance table rows not found.");
    }

    const attendanceClassMap = {'○': '0', '△': '1', '×': '2'};

    for (const choiceNum in attendances) {
      const status = attendances[choiceNum];
      const classSuffix = attendanceClassMap[status];
      const rowIndex = parseInt(choiceNum) - 1;

      if (classSuffix !== undefined && attendanceRows[rowIndex]) {
        const selector = `.oax-${classSuffix}`;
        const imageButton = attendanceRows[rowIndex].querySelector(selector);
        
        if (imageButton) {
          imageButton.click();
        } else {
          throw new Error(`Button not found with selector ${selector} in row ${rowIndex + 1}`);
        }
      } else {
          console.warn(`Skipping invalid choice number or status: ${choiceNum} / ${status}`);
      }
    }

    alert('入力が完了しました。内容を確認して送信してください。');

  } catch (error) {
    alert(`エラーが発生しました: ${error.message}`);
  }
}