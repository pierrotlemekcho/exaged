import React, { useState } from "react";
import { TextArea, Button } from "semantic-ui-react";
const TextField = ({ onSave, icon, value, loading, error, ...props }) => {
  const [currentValue, setCurrentValue] = useState(value || "");
  const [saving, setSaving] = useState(false);
  const [lastValue, setLastValue] = useState(value || "");

  // 1. We introduce some new state to keep track of
  const [saved, setSaved] = useState(true);
  const [saveError, setSaveError] = useState();
  return (
    <React.Fragment>
      <TextArea
        icon={{
          // 2. we swap our icon depending on the save state
          name: saveError ? "warning circle" : saved ? "check circle" : icon,
          // 3. let's change the icon color as well for better feedback
          color: saveError ? "red" : saved ? "green" : "grey",
        }}
        value={currentValue}
        loading={`${loading || saving}`}
        disabled={loading || saving}
        // 4. we will either show a validation error or a save error
        error={error || saveError}
        // 5. we probably don't want to show a saved icon when input changes
        onChange={(e) => {
          setSaved(false);
          setCurrentValue(e.target.value);
        }}
        {...props}
      />
      {!saved ? (
        <Button
          loading={saving}
          onClick={async (e) => {
            const val = currentValue;
            if (val !== lastValue) {
              setSaving(true);
              try {
                onSave && (await onSave(val));
                setSaved(true);
                setSaving(false);
                setLastValue(val);
              } catch (err) {
                // 6. let's save the error so we can let the user know a save failed
                setSaveError("Error Message");
              }
            }
          }}
        >
          Sauvegarder commentaire
        </Button>
      ) : (
        ""
      )}
    </React.Fragment>
  );
};
export default TextField;
