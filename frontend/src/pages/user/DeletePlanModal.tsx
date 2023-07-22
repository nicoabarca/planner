
import { memo, useState, useEffect, Fragment } from 'react'
import { Dialog, Transition } from '@headlessui/react'

interface DeletePlanModalProps {
  selectedPlanName: string | undefined
  isOpen: boolean
  onClose: Function
  deletePlan: Function
}

const DeletePlanModal = ({ selectedPlanName, isOpen, onClose, deletePlan }: DeletePlanModalProps): JSX.Element => {
  const [planName, setPlanName] = useState<string | undefined>('')

  useEffect(() => {
    if (planName !== selectedPlanName) {
      setPlanName(selectedPlanName)
    }
  }, [selectedPlanName])

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="modal relative" onClose={() => { onClose() } }>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:max-w-lg">
                <div className="bg-white pb-4 pt-5 sm:p-6 sm:pb-4">
                  <div className="justify-center sm:flex sm:items-start p-3">
                    <div className="mt-3 text-center sm:ml-4 sm:mt-0 ">
                      <Dialog.Title as="h3" className="text-lg font-normal leading-6 text-gray-900">
                        Vas a eliminar la malla <span className='font-semibold'>{selectedPlanName}</span>
                      </Dialog.Title>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-4 py-3 sm:flex sm:px-6">
                  <button
                    type="button"
                    className="bg-red-600 inline-flex grow justify-center rounded-md text-sm btn shadow-sm sm:ml-3 sm:w-auto hover:bg-red-700"
                    onClick={() => {
                      deletePlan()
                      onClose()
                    }}
                  >
                    Sí, eliminar
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  )
}

export default memo(DeletePlanModal)
