import React from 'react';
import { Target } from 'lucide-react';
import { FrontendTestCase } from '../types';
import { EditableSection } from '../../../shared/components/EditableSection';

interface TestCaseGoalProps {
  testCase: FrontendTestCase;
  editableTestCase: FrontendTestCase | null;
  isEditing: boolean;
  onEdit: () => void;
  onSave: () => void;
  onCancel: () => void;
  onGoalChange: (goal: string) => void;
}

export const TestCaseGoal: React.FC<TestCaseGoalProps> = ({
  testCase,
  editableTestCase,
  isEditing,
  onEdit,
  onSave,
  onCancel,
  onGoalChange
}) => {
  return (
    <EditableSection
      title="Test goal"
      isEditing={isEditing}
      onEdit={onEdit}
      onSave={onSave}
      onCancel={onCancel}
      editTitle="Edit goal"
    >
      <div className="flex items-center space-x-2 mb-4">
        <Target className="h-5 w-5 text-blue-600" />
      </div>
      {isEditing ? (
        <textarea
          value={editableTestCase?.goal || ''}
          onChange={(e) => onGoalChange(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
          placeholder="Enter test goal"
          rows={3}
        />
      ) : (
        <p className="text-gray-600">{testCase.goal}</p>
      )}
    </EditableSection>
  );
};
