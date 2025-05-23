import React, { useState } from 'react';
import { registerUser } from '../services/api';

function UserForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    age: '',
    experience: '',
    jobTitle: ''
  });
  
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState('');

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Clear error for this field
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };

  // Validate form data
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (formData.age && (isNaN(formData.age) || formData.age < 18 || formData.age > 100)) {
      newErrors.age = 'Age must be a number between 18 and 100';
    }
    
    if (formData.experience && (isNaN(formData.experience) || formData.experience < 0 || formData.experience > 50)) {
      newErrors.experience = 'Experience must be a number between 0 and 50';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    setApiError('');
    
    try {
      const response = await registerUser({
        name: formData.name,
        email: formData.email,
        age: formData.age ? parseInt(formData.age) : null,
        experience: formData.experience ? parseInt(formData.experience) : null,
        job_title: formData.jobTitle
      });
      
      setIsLoading(false);
      
      // Call the onSubmit callback with the user data
      onSubmit(response.user);
      
    } catch (error) {
      setIsLoading(false);
      setApiError(error.message || 'An error occurred. Please try again.');
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h4 className="mb-0">Candidate Information</h4>
            </div>
            <div className="card-body">
              {apiError && (
                <div className="alert alert-danger" role="alert">
                  {apiError}
                </div>
              )}
              
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="name" className="form-label">Full Name *</label>
                  <input
                    type="text"
                    className={`form-control ${errors.name ? 'is-invalid' : ''}`}
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Enter your full name"
                  />
                  {errors.name && <div className="invalid-feedback">{errors.name}</div>}
                </div>
                
                <div className="mb-3">
                  <label htmlFor="email" className="form-label">Email Address *</label>
                  <input
                    type="email"
                    className={`form-control ${errors.email ? 'is-invalid' : ''}`}
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="Enter your email address"
                  />
                  {errors.email && <div className="invalid-feedback">{errors.email}</div>}
                </div>
                
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="age" className="form-label">Age</label>
                    <input
                      type="number"
                      className={`form-control ${errors.age ? 'is-invalid' : ''}`}
                      id="age"
                      name="age"
                      value={formData.age}
                      onChange={handleChange}
                      placeholder="Enter your age"
                      min="18"
                      max="100"
                    />
                    {errors.age && <div className="invalid-feedback">{errors.age}</div>}
                  </div>
                  
                  <div className="col-md-6 mb-3">
                    <label htmlFor="experience" className="form-label">Years of Experience</label>
                    <input
                      type="number"
                      className={`form-control ${errors.experience ? 'is-invalid' : ''}`}
                      id="experience"
                      name="experience"
                      value={formData.experience}
                      onChange={handleChange}
                      placeholder="Years of experience"
                      min="0"
                      max="50"
                    />
                    {errors.experience && <div className="invalid-feedback">{errors.experience}</div>}
                  </div>
                </div>
                
                <div className="mb-3">
                  <label htmlFor="jobTitle" className="form-label">Current Job Title</label>
                  <input
                    type="text"
                    className="form-control"
                    id="jobTitle"
                    name="jobTitle"
                    value={formData.jobTitle}
                    onChange={handleChange}
                    placeholder="Enter your current job title"
                  />
                </div>
                
                <div className="d-grid gap-2">
                  <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Processing...
                      </>
                    ) : 'Continue to Interview Setup'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UserForm;
